"""ЛР 1. Экспертный подбор ПК по числовому бюджету. Только стандартный Python."""
from pathlib import Path

folder = Path(__file__).resolve().parent


def get_fact(text):
    name, value = text.split("=", 1)
    name, value = name.strip(), value.strip()
    if name == "" or value == "":
        raise ValueError("Нужен факт объект=значение")
    return name, value


def get_rule(text):
    if not text.startswith("ЕСЛИ "):
        raise ValueError("Правило должно начинаться с ЕСЛИ")
    left, right = text[5:].split(" ТО ")
    conditions = left.split(" И ")
    for condition in conditions:
        get_fact(condition)
    get_fact(right)
    return conditions, right


def load_rules(filename="rules.txt"):
    rules = []
    with open(folder / filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                get_rule(line)
                rules.append(line)
    return rules


def get_inputs(rules):
    # Результаты правил система выводит сама. Остальные объекты - входные.
    results = []
    for rule in rules:
        conditions, result = get_rule(rule)
        name, value = get_fact(result)
        results.append(name)
    inputs = {}
    for rule in rules:
        conditions, result = get_rule(rule)
        for condition in conditions:
            name, value = get_fact(condition)
            if name not in results:
                if name not in inputs:
                    inputs[name] = []
                if value not in inputs[name]:
                    inputs[name].append(value)
    return inputs


def show_facts(facts):
    print("\nРабочая база:")
    for name in facts:
        print(name, "=", facts[name])


def choose_value(name, values):
    # Номер пункта превращаем в значение факта из базы правил.
    print("\nВыберите:", name)
    for number, value in enumerate(values, 1):
        print(number, "-", value)
    while True:
        choice = input("Номер пункта (Enter = пока не знаю): ").strip()
        if choice == "":
            return ""
        if choice.isdigit() and 1 <= int(choice) <= len(values):
            return values[int(choice) - 1]
        print("Введите номер из списка.")


def find_question(rules, facts, inputs):
    # Ищем неизвестный входной объект в правиле без ложных условий.
    for rule in rules:
        conditions, result = get_rule(rule)
        possible = True
        missing = None
        for condition in conditions:
            name, value = get_fact(condition)
            if name in facts and facts[name] != value:
                possible = False
            if name not in facts and name in inputs:
                missing = name
        if possible and missing is not None:
            return missing
    return None


def run(rules, start, details=True, ask=True):
    facts = start.copy()
    inputs = get_inputs(rules)
    # Нельзя вводить готовые выводы вместо исходных сведений.
    for name in facts:
        if name not in inputs or facts[name] not in inputs[name]:
            raise ValueError("Неизвестный входной факт: " + name + "=" + facts[name])
    if details:
        show_facts(facts)
    while True:
        changed = False
        for rule in rules:
            conditions, result = get_rule(rule)
            suitable = True
            for condition in conditions:
                name, value = get_fact(condition)
                if name not in facts or facts[name] != value:
                    suitable = False
            if suitable:
                name, value = get_fact(result)
                if name not in facts:
                    facts[name] = value
                    changed = True
                    if details:
                        print("\nСработало:", rule)
                        show_facts(facts)
                elif facts[name] != value:
                    raise ValueError("Противоречие для объекта: " + name)
        if changed:
            continue  # Новый факт может запустить другое правило.
        if "заключение" in facts:
            if details:
                print("РЕКОМЕНДАЦИЯ:", facts["заключение"])
            return facts
        if not ask:
            return facts
        name = find_question(rules, facts, inputs)
        if name is None:
            print("Заключение не получено. Для этой ситуации нет подходящих правил.")
            return facts
        print("\nНе хватает сведений об объекте:", name)
        for number, option in enumerate(inputs[name], 1):
            print(number, "-", option)
        value = input("Номер, значение или факт объект=значение. Enter = сведений нет: ").strip()
        if value.isdigit() and 1 <= int(value) <= len(inputs[name]):
            value = inputs[name][int(value) - 1]
        if "=" in value:
            obj, value = get_fact(value)
            if obj != name:
                print("Сейчас запрашивается объект:", name)
                continue
        if value == "":
            print("Вывод завершён: новых сведений нет.")
            return facts
        if value not in inputs[name]:
            print("Неизвестное значение. Выберите один из вариантов.")
        else:
            facts[name] = value
            show_facts(facts)


def edit(rules):
    for i in range(len(rules)):
        print(i + 1, rules[i])
    action = input("1 = добавить, 2 = изменить, 3 = удалить, Enter = назад: ").strip()
    if action not in ["1", "2", "3"]:
        return
    if action == "1":
        rule = input("Новое правило: ").strip()
        get_rule(rule)
        rules.append(rule)
    else:
        index = int(input("Номер правила: ")) - 1
        if index < 0 or index >= len(rules):
            raise ValueError("Нет такого номера")
        if action == "2":
            rule = input("Новое правило: ").strip()
            get_rule(rule)
            rules[index] = rule
        else:
            rules.pop(index)
    with open(folder / "rules.txt", "w", encoding="utf-8") as file:
        for rule in rules:
            file.write(rule + "\n")
    print("Правила сохранены.")


# Какие детали входят в стоимость всего системного блока.
parts = ["процессор", "плата", "озу", "видеокарта", "SSD", "блок_питания", "кулер", "корпус"]
levels = ["эконом", "средний", "высокий"]


def load_prices():
    prices = {}
    with open(folder / "prices.txt", encoding="utf-8") as file:
        for line in file:
            if line.strip() and not line.startswith("#"):
                model, price = get_fact(line)
                prices[model] = int(price)
                if prices[model] < 0:
                    raise ValueError("Цена не может быть отрицательной")
    return prices


def get_total(facts, prices):
    total = 0
    for part in parts:
        if part not in facts:
            raise ValueError("Правила не подобрали компонент: " + part)
        model = facts[part]
        if model not in prices:
            raise ValueError("Нет цены для модели: " + model)
        total += prices[model]
    return total


def get_budget(text):
    text = text.replace(" ", "").replace("\u00a0", "").strip()
    if not text.isdigit() or int(text) <= 0:
        raise ValueError("Бюджет должен быть положительным целым числом, например 60000")
    return int(text)


def configure(rules, start):
    # Пользовательские ответы - входные факты. Модели выводят правила.
    budget = get_budget(start.get("бюджет", ""))
    answers = {}
    for name in ["производитель", "задача"]:
        options = get_inputs(rules).get(name, [])
        value = start.get(name, "")
        if value == "":
            value = choose_value(name, options)
        if value == "":
            print("Подбор завершён: новых сведений нет.")
            return {}
        if value not in options:
            raise ValueError("Недопустимое значение: " + name)
        answers[name] = value
    prices = load_prices()
    best = None
    minimum = None
    # Проверяем три уровня одной и той же базой правил.
    # Более высокий уровень предпочитается, только если хватает бюджета.
    for level in levels:
        candidate = answers.copy()
        candidate["уровень"] = level
        result = run(rules, candidate, details=False, ask=False)
        total = get_total(result, prices)
        if "заключение" not in result:
            raise ValueError("В базе правил нет итогового заключения")
        print("Вариант", level, "-", total, "руб.")
        if minimum is None or total < minimum:
            minimum = total
        if total <= budget:
            best = candidate
    if best is None:
        print("На выбранную задачу и производителя бюджета не хватает.")
        print("Минимальная сумма по этой базе:", minimum, "руб.")
        print("Не хватает:", minimum - budget, "руб.")
        return {}
    print("\nПодходит уровень:", best["уровень"])
    result = run(rules, best)
    total = get_total(result, prices)
    print("\n========== ВАША СБОРКА ==========")
    for part in parts:
        model = result[part]
        print(part + ": " + model + " - " + str(prices[model]) + " руб.")
    print("ИТОГО:", total, "руб.")
    print("Бюджет:", budget, "руб. Остаток:", budget - total, "руб.")
    print("Цены учебные, из prices.txt. Монитор, периферия и ОС не включены.")
    print("Для покупки проверить BIOS платы и размеры конкретной видеокарты.")
    result["бюджет"] = str(budget)
    result["стоимость"] = str(total)
    return result


def main():
    rules = load_rules()
    start = {}
    with open(folder / "facts.txt", encoding="utf-8") as file:
        for line in file:
            if line.strip() and not line.startswith("#"):
                name, value = get_fact(line)
                start[name] = value
    facts = {}
    print("Подбор системного блока по бюджету. Цены учебные, из prices.txt.")
    while True:
        print("\n1. Подобрать ПК (бюджет и вопросы)\n2. Показать факты\n3. Показать правила")
        print("4. Редактировать правила\n5. Ввести стартовые факты")
        print("6. Подбор по стартовым фактам\n0. Выход")
        choice = input("Выбор: ").strip()
        try:
            if choice == "0":
                break
            elif choice == "1":
                while True:
                    text = input("Бюджет в рублях (например 60000). Enter = назад: ").strip()
                    if text == "":
                        break
                    try:
                        budget = get_budget(text)
                    except ValueError as error:
                        print(error)
                        continue
                    start = {"бюджет": str(budget)}
                    facts = configure(rules, start)
                    break
            elif choice == "2":
                show_facts(facts)
            elif choice == "3":
                for number, rule in enumerate(rules, 1):
                    print(number, rule)
            elif choice == "4":
                edit(rules)
                facts = {}
            elif choice == "5":
                print("Пример: бюджет=60000, производитель=AMD, задача=игры")
                text = input("Факты через запятую: ")
                new_start = {}
                for item in text.split(","):
                    if item.strip():
                        name, value = get_fact(item)
                        if name not in ["бюджет", "производитель", "задача"] or name in new_start:
                            raise ValueError("Неизвестный или повторный объект: " + name)
                        new_start[name] = value
                start = new_start
                facts = {}
            elif choice == "6":
                if "бюджет" not in start:
                    text = input("Укажите бюджет в рублях. Enter = сведений нет: ").strip()
                    if text == "":
                        print("Новых сведений нет. Подбор завершён.")
                        continue
                    start["бюджет"] = str(get_budget(text))
                facts = configure(rules, start)
            else:
                print("Нет такого пункта.")
        except ValueError as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
