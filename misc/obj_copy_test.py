import copy
def flip_horizontal(maty1):
    matrix = copy.deepcopy(maty1)
   # print(id(maty1))
    #print(maty1)
   # print(id(matrix))
    #print()
    m = len(matrix)
    n = len(matrix[0])

    i = 0
    j = m-1

    while i < j:
        swap_rows(i,j,matrix)
        print(matrix)
        print(maty1)
        i += 1
        j -= 1
    print()
    #print(id(maty1))
    #print(maty1)
    #print(id(matrix))
    return matrix

def swap_rows(i,j,matrix):
    #print(id(matrix))
    n = len(matrix[0])

    for k in range(n):
        b_el = matrix[j][k]
        matrix[j][k] = matrix[i][k]
        matrix[i][k] = b_el


if __name__ == '__main__':
    in_mat = [[1,2,3],[4,5,6],[7,8,9]]
    f_mat = flip_horizontal(in_mat)
    print(in_mat)
    print(f_mat)
