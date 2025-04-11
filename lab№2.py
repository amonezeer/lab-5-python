while True:
    operation = input("Оберіть операцію ('~' - округлення, '#' - перевірка кутів трапеції, 'q' - вихід ): ")

    if operation == 'q':
        print("Завершення програми.")
        break

    if operation == '~':
        num_str = input("Введіть число для округлення: ")
        if num_str.replace('.', '', 1).isdigit():
            num = float(num_str)
            print(f"Округлене значення: {round(num)}")
        else:
            print("[Помилка]: введене значення не є числом!")

    elif operation == '#':
        angles = []
        for i in range(4):
            angle_str = input(f"Введіть кут {i + 1}: ")
            if angle_str.replace('.', '', 1).isdigit():
                angles.append(float(angle_str))
            else:
                print("[Помилка]: введене значення не є числом!")
                break
        else:
            if sum(angles) == 360 and (angles[0] == angles[1] and angles[2] == angles[3]):
                print("Можна утворити рівнобічну трапецію.")
            else:
                print("Ці кути не підходять для рівнобічної трапеції.")

    else:
        print("[Помилка]: невідома операція!")