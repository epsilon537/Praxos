#!/usr/bin/env python3
import sys
import getopt

class Opcode:
    def __init__(self, instr, operand, opType, shift):
        self.op = instr
        self.op <<= 29
        self.op |= operand
        self.opShift = shift
        self.operandType = opType

mnemonicMap = {}
mnemonicMap["ADD"] = Opcode(0, 0, 29, 0)
mnemonicMap["ADD#"] = Opcode(1, 0, 29, 0)
mnemonicMap["SUB"] = Opcode(4, 0, 29, 0)
mnemonicMap["SUB#"] = Opcode(5, 0, 29, 0)
mnemonicMap["BUSR"] = Opcode(8, 0, 32, 0)
mnemonicMap["BUSRB0"] = Opcode(8, 0x10000000, 28, 0)
mnemonicMap["BUSRB1"] = Opcode(9, 0, 28, 0)
mnemonicMap["BUSRH0"] = Opcode(9, 0x10000000, 28, 0)
mnemonicMap["BUSRB2"] = Opcode(10, 0, 28, 0)
mnemonicMap["BUSRB3"] = Opcode(12, 0, 28, 0)
mnemonicMap["BUSRH1"] = Opcode(14, 0, 28, 0)
mnemonicMap["BUSRW"] = Opcode(15, 0x10000000, 28, 0)
mnemonicMap["ILD#"] = Opcode(16, 0, 32, 0)
mnemonicMap["LD#"] = Opcode(24, 0, 32, 0)
mnemonicMap["LD"] = Opcode(32, 0, 29, 0)
mnemonicMap["AND"] = Opcode(34, 0, 29, 0)
mnemonicMap["OR"] = Opcode(36, 0, 29, 0)
mnemonicMap["XOR"] = Opcode(38, 0, 29, 0)
mnemonicMap["OUT"] = Opcode(40, 0, 16, 0)
mnemonicMap["IN"] = Opcode(44, 0, 16, 0)
mnemonicMap["ST"] = Opcode(48, 0, 29, 0)
mnemonicMap["IST"] = Opcode(52, 0, 29, 0)
mnemonicMap["ILD"] = Opcode(56, 0, 29, 0)
mnemonicMap["BUSW"] = Opcode(64, 0, 32, 0)
mnemonicMap["BUSWB0"] = Opcode(64, 0x10000000, 28, 0)
mnemonicMap["BUSWB1"] = Opcode(65, 0, 28, 0)
mnemonicMap["BUSWH0"] = Opcode(65, 0x10000000, 28, 0)
mnemonicMap["BUSWB2"] = Opcode(66, 0, 28, 0)
mnemonicMap["BUSWB3"] = Opcode(68, 0, 28, 0)
mnemonicMap["BUSWH1"] = Opcode(70, 0, 28, 0)
mnemonicMap["BUSWW"] = Opcode(71, 0x10000000, 28, 0)
mnemonicMap["IADD#"] = Opcode(72, 0, 16, 16)
mnemonicMap["SHR0"] = Opcode(80, 0, 0, 0)
mnemonicMap["SHR1"] = Opcode(81, 0, 0, 0)
mnemonicMap["SHRX"] = Opcode(82, 0, 0, 0)
mnemonicMap["ROR"] = Opcode(83, 0, 0, 0)
mnemonicMap["SHL0"] = Opcode(84, 0, 0, 0)
mnemonicMap["SHL1"] = Opcode(85, 0, 0, 0)
mnemonicMap["SHLX"] = Opcode(86, 0, 0, 0)
mnemonicMap["ROL"] = Opcode(87, 0, 0, 0)
mnemonicMap["JAL"] = Opcode(88, 0, 16, 0)
mnemonicMap["LDI"] = Opcode(96, 0, 16, 0)
mnemonicMap["ANDI"] = Opcode(98, 0, 16, 0)
mnemonicMap["ORI"] = Opcode(100, 0, 16, 0)
mnemonicMap["XORI"] = Opcode(102, 0, 16, 0)
mnemonicMap["POP"] = Opcode(104, 0x10000, 0, 0) # w = 1
mnemonicMap["PUSH"] = Opcode(108, 0x1FFFFFFF, 0, 0) # // w = -1, y = -1
mnemonicMap["BRA"] = Opcode(112, 0, 29, 0)
mnemonicMap["BR"] = Opcode(112, 0, 29, 0)
mnemonicMap["BRZ"] = Opcode(113, 0, 29, 0)
mnemonicMap["BRNZ"] = Opcode(114, 0, 29, 0)
mnemonicMap["BRP"] = Opcode(115, 0, 29, 0)
mnemonicMap["BRN"] = Opcode(116, 0, 29, 0)
mnemonicMap["BRIN"] = Opcode(117, 0, 29, 0)
mnemonicMap["BRIO"] = Opcode(118, 0, 29, 0)
mnemonicMap["NOP"] = Opcode(119, 0, 0, 0)
mnemonicMap["STI"] = Opcode(120, 0, 16, 0)

workingBuffer = [] #Working Buffer of UnpackedLines

labelMap = {} #Map of labels
progCodeList = [] #Will hold the program code values

class operand:
    def __init__(self, s):
        self.str = s

class UnpackedLine:
    def __init__(self, ln):
        self.line = ln
        self.label= ""
        self.directive = ""
        self.mnemonic = ""
        self.operands = []
        self.comment = ""

#Returns False if failed.
def FirstPass(srcCodeLines):
    instrCount = 0
    lineNum=0

    for srcCodeLine in srcCodeLines:
        lineNum += 1
        srcCodeLine = srcCodeLine.upper()
        words = srcCodeLine.split()

        unpackedLine = UnpackedLine(lineNum)
        
        for word in words:
            #Directive:
            if word[0]=='.':
                if unpackedLine.directive == "":
                    unpackedLine.directive = word
                else:
                    print("Multiple directives on line %d"%(lineNum))
                    return False    
            #Label:                
            elif word[0]=='@':
                    if unpackedLine.label == "":
                        word = word[1:]
                        unpackedLine.label = word
                        if word in labelMap.keys():
                            print("Duplicate label %s on line %d"%(word, lineNum))
                            return False
                        else:
                            labelMap[word] = instrCount
                    else:
                        print("Multiple labels on line %d"%(lineNum))
                        return False
            #Comment:
            elif word[0]==';':
                break #Skip further processing of words on this line
            else:
                #Mnemonic:
                if unpackedLine.mnemonic == "":
                    if word in mnemonicMap.keys():
                        instrCount += 1
                        unpackedLine.mnemonic = word
                    else:
                        print("Error no valid mnemonic on line %d"%(lineNum))
                        return False
                else:
                    if word in mnemonicMap.keys():
                        print("Error duplicate mnemonic on line %d"%(lineNum))
                        return False
                    else:
                        #Operands:
                        unpackedLine.operands.append(operand(word))
            
            if unpackedLine.directive == ".EQU":
                #.EQUs require three words
                if len(words) < 3:
                    print("Invalid equate on line %"%(lineNum))
                    return False
                
                equName = words[1]
                #.EQU labels can't start with these characters
                if equName[0] in ['0123456789;.@+-/*~&|#']:
                    print("Invalid equate on line %d"%(lineNum))
                    return False
                
                if equName in mnemonicMap.keys():
                    print("Reserved word in .EQU on line %d"%(lineNum))
                    return False
                
                if equName in labelMap.keys():
                    print(".EQU name already in use on line %d"%(lineNum))
                    return False

                equValueStr = words[2]
                try:
                    if equValueStr[0] == '$':
                        equValue = int(equValueStr[1:], 16)
                    else:
                        equValue = int(equValueStr)
                    
                    labelMap[equName] = equValue
                except ValueError:
                    print("Invalid value for .EQU on line %d"%(lineNum))
                    return False

                break #Skip further word processing on this line
            
        if (unpackedLine.label != "") and (unpackedLine.mnemonic == ""):
            print("Error no instruction at label %s"%(unpackedLine.label))
            return False

        #Add processed line to workingBuffer
        workingBuffer.append(unpackedLine)

    return True

#Returns emitted instruction count, negative on error
def SecondPass():
    error = False
    operand = 0
    instrCount = 0
    
    for unpackedLine in workingBuffer:
        operand = 0
        if unpackedLine.mnemonic != "":
            opCode = mnemonicMap[unpackedLine.mnemonic]
            instrCode = opCode.op
            max = (1 << opCode.operandType)

            if opCode.operandType != 0:
                operandStr = unpackedLine.operands[0].str
                
                try:
                    if operandStr[0] == '$':
                        operand = int(operandStr[1:],16)
                        if (opCode.operandType != 32) and (operand >= max):
                            operand -= max * 2
                    else:
                        operand = int(operandStr)
                        if (opCode.operandType != 32) and ((operand >= max) or (operand < -max)):
                            print("operand out of range on line %d"%(unpackedLine.line+1))
                            return -1
                        #Convert negative integers to unsigned
                        if operand < 0:
                            operand += (1<<32)

                except ValueError:
                    if operandStr in labelMap.keys():
                        if unpackedLine.mnemonic[0] == 'B': # relative branch
                            operand = labelMap[operandStr]
                            operand = operand - instrCount - 1 # apply a -1 offset to account for the branch delay slot
                            operand &= max-1
                        else:
                            operand = labelMap[operandStr]
                            if opCode.operandType != 32:
                                operand &= max-1
                    else:
                        print("Could not parse operand on line %d"%(unpackedLine.line+1))
                        return -1
                
                operand <<= opCode.opShift
                operand &= 0xffffffff
                instrCode += operand
            
            progCodeList.append(instrCode)
            instrCount += 1

    return instrCount

def usage():
    print("Usage: praxos_asm.py [-h(elp)] -p <program memory size> -s <praxos.asm> -o <outfile basename>")

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:s:o:", ["help", "pmSize=", "source=","outfile="])
    except getopt.GetoptError as err:
        # print help information and exit:
        usage()
        sys.exit(2)

    pmSize = None
    inFile = None
    outFile = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-s", "--source"):
            inFile = a
        elif o in ("-o", "--outfile"):
            outFile = a
        elif o in ("-p", "--pmSize"):
            try:
                pmSize = int(a)
            except ValueError:
                print("program memory size must be integer value.")
                usage()
                sys.exit(-1)
        else:
            assert False, "unhandled option"
    
    if pmSize is None:
        print("-p <program memory size> argument is required.")
    
    if inFile is None:
        print("-s <praxos.asm> argument is required.")
 
    if outFile is None:
        print("-o <outfile basename> argument is required.")
 
    if not (pmSize and inFile and outFile):
        usage()
        sys.exit(-1)

    try:
        f = open(inFile, "r")
        srcCodeLines = f.readlines()
    except:
        print("Error, could not open file %s"%(inFile))
        sys.exit(-1)
    
    print("\nFirst pass...")
    if not FirstPass(srcCodeLines):
        print("First pass failed.")
        sys.exit(-1)

    print("Second pass...")
    count = SecondPass()
    if count <= 0:
        print("Second pass failed")
        sys.exit(-1)

    if count >= pmSize:
        print("Program size %d doesn't fit in pmSize %d"%(count, pmSize))
        sys.exit(-1)
        
    try:
        #.mem file
        with open(outFile+".mem", 'w') as f:
            for p in progCodeList:
                f.write("{:09X}\n".format(p))
        
        #.h file
        with open(outFile+".h", 'w') as f:
            f.write("#ifndef %s_h\n"%(outFile))
            f.write("#define %s_h\n"%(outFile))
            f.write("#define %s {\\\n"%(outFile.upper()))
            for p in progCodeList[:-1]:
                f.write("0x{:09X}ULL,\\\n".format(p))

            f.write("0x{:09X}ULL}}\n".format(progCodeList[-1]))
            f.write("#endif\n")
        
        #.py file
        with open(outFile+".py", 'w') as f:
            f.write("%s = [\n"%(outFile.upper()))
            for p in progCodeList[:-1]:
                f.write("0x{:09X},\n".format(p))
            f.write("0x{:09X}]\n".format(progCodeList[-1]))
    except:
        print("Error writing output file: %s"%(outFile))
       
    print("Done.")
               
