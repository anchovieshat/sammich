import sys
import struct

class Instruction:
    def __init__(self, a, b, c, op, val=0):
        self.a = a
        self.b = b
        self.c = c
        self.op = op
        self.val = val

class CPU:
    def __init__(self, filename):
        self.reg = [0 for i in range(8)]
        self.arrays = []

        self.arrays.append([])

        f = open(filename, 'rb')
        fbytes = f.read()

        values = []
        for val, in struct.iter_unpack('>I', fbytes):
            values.append(val)

        for val in values:
            self.arrays[0].append(val)

        self.pc = 0
        self.next_array = 1
        self.running = True

    def cmov(self, dest, src, cond):
        if self.reg[cond] != 0:
            self.reg[dest] = self.reg[src]

    def aget(self, dest, arr, index):
        self.reg[dest] = self.arrays[self.reg[arr]][self.reg[index]]

    def aset(self, arr, index, val):
        self.arrays[self.reg[arr]][self.reg[index]] = self.reg[val]

    def add(self, dest, var1, var2):
        self.reg[dest] = self.reg[var1] + self.reg[var2]

    def mul(self, dest, var1, var2):
        self.reg[dest] = self.reg[var1] * self.reg[var2]

    def div(self, dest, var1, var2):
        self.reg[dest] = self.reg[var1] / self.reg[var2]

    def nand(self, dest, var1, var2):
        self.reg[dest] = int(not (self.reg[var1] & self.reg[var2]))

    def hlt(self):
        self.running = False

    def new_arr(self, dest, size):
        self.arrays[self.next_array] = []
        self.reg[dest] = self.next_array
        self.next_array += 1

    def del_arr(self, dest):
        self.arrays[self.reg[dest]].pop()

    def out(self, val):
        print(chr(self.reg[val]), end='')

    def uin(self, val):
        print("reading to reg[{}]".format(val))

    def load(self, arr, npc):
        #print("arr: {}, pc: {}".format(arr, npc))
        narr = self.arrays[self.reg[arr]]
        if narr != 0:
            self.arrays[0] = narr
        self.pc = npc

    def move(self, dest, val):
        #print("dest: {}, value: {}".format(dest, val))
        self.reg[dest] = val

    def unknown(self, val):
        print("unknown inst: {}".format(val))
        sys.exit(1)

    def dump_reg(self):
        for counter, r in enumerate(self.reg):
            print("Register {}: {}".format(counter, r))

    def decode(self, inst):
        op = (inst & 0b11110000000000000000000000000000) >> 28
        if op == 13:
            a = (inst & 0b00001110000000000000000000000000) >> 25
            val = inst & 0b00000001111111111111111111111111
            return Instruction(a, -1, -1, op, val=val)

        a = (inst & 0b00000000000000000000000111000000) >> 6
        b = (inst & 0b00000000000000000000000000111000) >> 3
        c = (inst & 0b00000000000000000000000000000111)

        return Instruction(a, b, c, op)

    def exec(self, inst):
        a = inst.a
        b = inst.b
        c = inst.c
        op = inst.op
        val = inst.val

        name = {
            0: "CMOV",
            1: "AGET",
            2: "ASET",
            3: "ADD",
            4: "MUL",
            5: "DIV",
            6: "NAND",
            7: "HLT",
            8: "NEW_ARR",
            9: "DEL_ARR",
            10: "OUT",
            11: "IN",
            12: "LOAD",
            13: "MOVE",
        }

        one = {
            9: self.del_arr,
            10: self.out,
            11: self.uin,
        }
        two = {
            8: self.new_arr,
            12: self.load,
        }
        three = {
            0: self.cmov,
            1: self.aget,
            2: self.aset,
            3: self.add,
            4: self.mul,
            5: self.div,
            6: self.nand,
        }

        if op > -1 and op < 7:
            three[op](a, b, c)
            print("{}: {}, {}, {}".format(name[op], a, b, c))
        elif op == 8 or op == 12:
            two[op](b, c)
            print("{}: {}, {}".format(name[op], b, c))
        elif op == 9 or op == 10 or op == 11:
            one[op](c)
            print("{}: {}".format(name[op], c))
        elif op == 7:
            self.hlt()
            print("{}".format(name[op]))
        elif op == 13:
            self.move(a, val)
            print("MOVE {} -> Reg[{}]".format(val, a))
        elif op > 13:
            self.unknown(op)

    def test_decode(self):
        test =  self.decode(0b00000000000000000000000011010001)
        test2 = self.decode(0b11010110000000000000000000001000)
        test3 = self.decode(0b11000000000000000000000100100100)

        success = "failed"
        if test.a == 0b011 and test.b == 0b010 and test.c == 0b001 and test.op == 0:
            success = "success"

        print("test 1 [CMOV]: {}".format(success))

        success = "failed"
        if test2.a == 0b011 and test2.op == 13 and test2.val == 0b1000:
            success = "success"

        print("test 2 [MOVE]: {}".format(success))

        success = "failed"
        if test3.a == 0b100 and test3.b == 0b100 and test3.c == 0b100 and test3.op == 12:
            success = "success"

        print("test 3 [LOAD]: {}".format(success))

    def run(self):
        #while self.running == True:
        for i in range(20):
            inst = self.arrays[0][self.pc]
            self.pc += 1
            self.exec(self.decode(inst))
            self.dump_reg()
            print()

if len(sys.argv) != 2:
    print("Needs a file to run!")
    sys.exit(1)

cpu = CPU(sys.argv[1])
cpu.run()
