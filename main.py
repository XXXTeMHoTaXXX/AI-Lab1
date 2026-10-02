from pathlib import Path

# Папка, в которой находится main.py.
folder = Path(__file__).resolve().parent


def get_fact(text):
    # Разделяем "озу=DDR5" на имя объекта и значение.
    name, value = text.split("=")
    name = name.strip()
    value = value.strip()
    if name == "" or value == "":
        raise ValueError("Введите объект=значение")
    return name, value


def get_rule(text):
    # Условия слева от ТО, результат справа.
    if not text.startswith("ЕСЛИ "):
        raise ValueError("Правило должно начинаться с ЕСЛИ")
    left, right = text[5:].split(" ТО ")
    conditions = left.split(" И ")
    for condition in conditions:
        get_fact(condition)  # Проверяем формат каждого условия.
    get_fact(right)
    return conditions, right


def show_facts(facts):
    print("\nРабочая база:")
    for name in facts:
        print(name, "=", facts[name])


def run(rules, start):
    facts = start.copy()
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
                    print("\nСработало:", rule)
                    show_facts(facts)
                elif facts[name] != value:
                    print("Противоречие в правилах для объекта:", name)
                    return facts
        if changed:
            continue  # Повторяем проход: появились новые факты.
        if "совместимость" in facts:
            print("\nСовместимость CPU, платы и ОЗУ:", facts["совместимость"])
            return facts
        print("\nНи одно правило не добавило новых фактов.")
        text = input("Введите новые сведения (например, озу=DDR5). Enter = сведений нет: ")
        if text.strip() == "":
            print("Вывод завершён: новых сведений нет.")
            return facts
        name, value = get_fact(text)
        if name in facts:
            print("Этот объект уже известен. Для изменения используйте пункт 5.")
        else:
            facts[name] = value
            show_facts(facts)


def edit(rules):
    for i in range(len(rules)):
        print(i + 1, rules[i])
    action = input("1 = добавить, 2 = изменить, 3 = удалить, Enter = назад: ")
    if action not in ["1", "2", "3"]:
        return
    if action == "1":
        rule = input("Новое правило: ")
        get_rule(rule)
        rules.append(rule)
    else:
        index = int(input("Номер правила: ")) - 1
        if index < 0 or index >= len(rules):
            raise ValueError("Нет такого номера")
        if action == "2":
            rule = input("Новое правило: ")
            get_rule(rule)
            rules[index] = rule
        else:
            rules.pop(index)
    with open(folder / "rules.txt", "w", encoding="utf-8") as file:
        for rule in rules:
            file.write(rule + "\n")
    print("Правила сохранены.")


# Загружаем правила из отдельного файла.
rules = []
with open(folder / "rules.txt", encoding="utf-8") as file:
    for line in file:
        if line.strip() != "":
            rules.append(line.strip())

# Загружаем начальные факты.
start = {}
with open(folder / "facts.txt", encoding="utf-8") as file:
    for line in file:
        if line.strip() != "":
            name, value = get_fact(line)
            start[name] = value
facts = start.copy()

# Главное меню.
while True:
    print("\n1. Запустить вывод\n2. Показать факты\n3. Показать правила")
    print("4. Редактировать правила\n5. Ввести стартовые факты\n0. Выход")
    choice = input("Выбор: ")
    try:
        if choice == "0":
            break
        elif choice == "1":
            facts = run(rules, start)
        elif choice == "2":
            show_facts(facts)
        elif choice == "3":
            for rule in rules:
                print(rule)
        elif choice == "4":
            edit(rules)
        elif choice == "5":
            text = input("Факты через запятую: ")
            new_start = {}
            for item in text.split(","):
                if item.strip() != "":
                    name, value = get_fact(item)
                    new_start[name] = value
            start = new_start
            facts = start.copy()
            show_facts(facts)
        else:
            print("Нет такого пункта.")
    except ValueError:
        print("Ошибка ввода. Проверьте формат и номер.")
