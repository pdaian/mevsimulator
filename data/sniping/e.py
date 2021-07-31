import csv

def tt (a):
    return int(a, 16)

with open('onlytribe.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        # if {row[3]} == '\\xc7283b66eb1eb5fb86327f08e1b5816b0720212b'
        # print(type(row[2]))
        # print(type('0xef764bac8a438e7e498c2e5fccf0f174c3e3f8db'))
        # assert(row[2] != '0xef764bac8a438e7e498c2e5fccf0f174c3e3f8db')
        # print(int(row[2], 16))
        print(f'// transaction {row[0]} block {row[1]}\n {tt(row[2])} swaps for {tt(row[3])} by providing {row[4]} {tt(row[5])} and {row[6]} {tt(row[7])} with a change 0 fee {row[8]} ;')
        line_count += 1
    # print(f'Processed {line_count} lines.')



# // transaction 0x1c9b5b4731c8fb05a471752d6179aec4543d8f9f4c88148461d26c3a32738761 block 11920579
# 697323163401596485410334513241460920685086001293 swaps for 1212984059034912911801913882730558476698418007999 by providing 200000000000000000000 1097077688018008265106216665536940668749033598146 and 0 1212984059034912911801913882730558476698418007999 with change 0 fee 1671587031433 ;