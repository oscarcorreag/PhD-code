from canditates_list import CandidatesList

if __name__ == '__main__':
    cl = CandidatesList(5)
    cl.append(8)
    cl.append(6)
    cl.append(2)
    print(cl)
    cl[1] = 10
    print(cl)

    cl2 = CandidatesList(5)
    cl2.append([9, 2])
    cl2.append([3, 4])
    print(cl2)
    cl2[0][0] = 10
    print(cl2)