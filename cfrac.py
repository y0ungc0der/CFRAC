import random
import time
import math
import mpmath

# Вычисление символа Якоби 
def JacobiSymbol(a, n):
    g = 1
    s = 0

    while(a != 0 and a != 1):

        k = 0

        while (a & 1) == 0:
            a >>= 1
            k += 1

        if (k & 1) == 0:
            s = 1
        else:
            temp = n % 8
            if (temp == 1) or (temp == 7):
                s = 1
            elif (temp == 3) or (temp == 5):
                s = -1

        if a == 1:
            return g*s

        if(n % 4 == 3) and (a % 4 == 3):
            s -= (s << 1)

        a, n = n % a, a
        g = g*s

    a *= g
    return a

# Построение базы простых чисел
def ReadingFile(name, M, n):
    
    text = ""
    with open(name) as file:
        text = file.read()

    temp_text = text.split()

    num_list = []

    for num in range(1000000):
        if (len(num_list) < M):
            temp = int(temp_text[num])

            #  Добавляе в базу такие значения temp, что n- квадратичный вычет по модулю temp
            if (JacobiSymbol(n, temp) == 1):
                 num_list.append(temp)
        else:
            return num_list

    return num_list

# Проверка s на гладкость
def CheckForSmoothness(s, B):

    list_alph = []
    temp = 0

    list_alph.append(0)

    # Вычисление колличества повторений числа 2 в разложении числа s
    while (s&1) == 0:
        s >>= 1
        list_alph[0] += 1

    size = len(B)
    for i in range(2, size):
        temp = B[i]
        list_alph.append(0)

        # Пока s делится на B[i], то увеличиваем степень для этого значения B[i]
        while (s % temp == 0):
            s /= temp
            list_alph[len(list_alph) - 1] += 1

    if(s == 1):
        return list_alph
    return False

# Сделать бинарный вектор
def MakeBinVector(vector):

    bin_vector = 0

    for i in range(len(vector)):
        bin_vector |= ((vector[i]%2) << (len(vector) - 1 - i))

    return bin_vector

# Поиск B-гладких числителей подходящих дробей
def FactorIntoContinuedFraction(n, B, h_2):

    Matrix = []
    BinMatrix = {}

    mpmath.mp.dps = 100000  # содержит текущую точность (в цифрах)
    q = mpmath.mp.sqrt(n)

    prev_prev_P = 1
    prev_P = int(q)
    list_P = []

    prev_a = prev_P
    cur_a = prev_P

    q = 1/(q - cur_a)
    prev_a = cur_a
    cur_a = int(q)

    list_alph = CheckForSmoothness((prev_P*prev_P)%n, B)
    if (list_alph != False):
            Matrix.append(list_alph)
            list_P.append(prev_P)
            print(f"P = {next_P%n}  ::  P^2 (mod n) = {(next_P*next_P)%n}")
            # print(Matrix[0])

    j = 0
    while (len(list_P) < h_2):
        next_P = prev_P * cur_a + prev_prev_P

        list_alph = CheckForSmoothness((next_P*next_P)%n, B)

        if (list_alph != False):
            vector = [0]
            vector.extend(list_alph)
            bin_vector = MakeBinVector(vector)
            Matrix.append(vector)
            print(f"{j + 1}: P = {next_P%n}  ::  P^2 (mod n) = {(next_P*next_P)%n}")
            # print(Matrix[j])
            BinMatrix.update({j : bin_vector})
            j += 1
            list_P.append(next_P)
          
        else:
            list_alph = CheckForSmoothness(abs(((next_P*next_P)%n) - n), B)

            if (list_alph != False):
                vector = [1]
                vector.extend(list_alph)
                bin_vector = MakeBinVector(vector)
                Matrix.append(vector)
                print(f"{j + 1}: P = {next_P%n}  ::  P^2 (mod n) = {(next_P*next_P)%n-n}")
                # print(Matrix[j])
                BinMatrix.update({j : bin_vector})
                j += 1
                list_P.append(next_P)
                

        prev_prev_P = prev_P
        prev_P = next_P

        q = 1/(q - cur_a)
        prev_a = cur_a
        cur_a = int(q)

    return list_P, Matrix, BinMatrix

# исключить одинаковые элементы из списка
def ExcludeSameElements(list_elem):

    i = 0
    while (i < len(list_elem)):
        val = list_elem[i]
        count = list_elem.count(val)
        if (count&1) == 1:
            count -= 1
                
        camein = False
        for j in range(count):
            list_elem.remove(val)
            camein = True

        if (camein == True):
            i -= 1
        i += 1

    return list_elem

# найти нулевую сумму векторов
def GaussMethod(BinMatrix):

    dict_vect_sum = {}

    for i in range(len(BinMatrix)):
        dict_vect_sum.update({i : [i]})


    key = max(BinMatrix, key=BinMatrix.get)
    max_val = BinMatrix[key]

    bit = 1
    while (bit < max_val):
        bit <<= 1

    if(bit > max_val):
        bit >>= 1

    # метод Гаусса
    while (len(BinMatrix) > 1):
        key = min(BinMatrix, key=BinMatrix.get)

        if(BinMatrix[key] == 0):
            # исключаем одинаковые элементы из суммы
            return ExcludeSameElements(dict_vect_sum[key])

        key = max(BinMatrix, key=BinMatrix.get)
        max_val = BinMatrix.pop(key)

        while (bit & max_val) == 0:
            bit >>= 1

        for i in BinMatrix.keys():
            if (BinMatrix[i] & bit) == 0:
                continue

            BinMatrix[i] ^= max_val
            
            dict_vect_sum[i].extend(dict_vect_sum[key])
            dict_vect_sum[i] = ExcludeSameElements(dict_vect_sum[i])

        dict_vect_sum.pop(key)

    return False

# создать число S для метода непрерывных дробей
def MakeNumberS(n, sum_vectors_idx, list_P):

    s = 1
    for i in sum_vectors_idx:
        s *= list_P[i]

    s %= n
    print(f"S = {s}")
    return s

# создать число T для метода непрерывных дробей
def MakeNumberT(n, B, sum_vectors_idx, Matrix):

    t = 1
    for i in range(1, len(B)):
        deg_sum = 0

        for j in sum_vectors_idx:
            deg_sum += Matrix[j][i]

        deg_sum >>= 1
        t *= pow(B[i], deg_sum)

    t %= n
    print(f"T = {t}")
    return t

# метод непрерывных дробей
def ContinuousFractionMethod(n):
    
    B = [-1]
    B.extend(ReadingFile("_primes1.txt", 100, n))
    # B.extend(ReadingFile("_primes1.txt", 6292, n))
    # B.extend(ReadingFile("_primes1.txt", 683675, n))
    # B.extend(ReadingFile("_primes1.txt", 855660321, n))

    h = len(B) - 1
    print(f"{h} - размер базы")
    # print(f"База: {B}")

    ret = FactorIntoContinuedFraction(n, B, h + 2)

    list_P = ret[0]
    Matrix = ret[1]
    BinMatrix = ret[2].copy()

    sum_vectors_idx = GaussMethod(BinMatrix)

    s = MakeNumberS(n, sum_vectors_idx, list_P)
    t = MakeNumberT(n, B, sum_vectors_idx, Matrix)

    if (s%n == t%n) or (s%n == (t%n) - n):
        print("Error")

    result = math.gcd(abs(s - t), n)

    return result

random.seed(time.time)

# n =  21299881
n =  944159
# n = 41654651842558664537
# n = 1505467596630152500666692430893290880361
# n = 23317141957300804502327510552585291906934171645219580845521453783840064367747583

ret = ContinuousFractionMethod(n)

print(f"{ret} - делитель числа {n}")