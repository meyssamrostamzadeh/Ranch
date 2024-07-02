
        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

huart1:
        DS8 64

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

huart2:
        DS8 64


        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

sender:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

lAssign:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

rAssign:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

leftReq:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

rightReq:
        DS8 4
		
request:
        PUSH     {R7,LR}        
          CFI R14 Frame(CFA, -4)
          CFI CFA R13+8

        LDR.N    R0,??DataTable5
        LDR      R0,[R0, #+0]   
        CMP      R0,#+1         
        BNE.N    ??request_0    

        LDR.N    R1,??DataTable5_1
        LDR      R0,[R1, #+0]   
        CMP      R0,#+0         
        BNE.N    ??request_1    

        MOVS     R0,#+1         
        STR      R0,[R1, #+0]   

        LDR.N    R0,??DataTable5_2
        LDR      R0,[R0, #+0]   
        CMP      R0,#+0         
        BNE.N    ??request_1    

        MOVS     R1,#+1         
        LDR.N    R0,??DataTable5_3
        STR      R1,[R0, #+0]   

          CFI FunCall philL_permit
        BL       philL_permit   
        B.N      ??request_1    


??request_0:
        LDR.N    R1,??DataTable5_4
        LDR      R0,[R1, #+0]   
        CMP      R0,#+0         
        BNE.N    ??request_1    

        MOVS     R0,#+1         
        STR      R0,[R1, #+0]   

        LDR.N    R0,??DataTable5_3
        LDR      R0,[R0, #+0]   
        CMP      R0,#+0         
        BNE.N    ??request_1    

        MOVS     R1,#+1         
        LDR.N    R0,??DataTable5_2
        STR      R1,[R0, #+0]   

          CFI FunCall philR_permit
        BL       philR_permit   


??request_1:
        POP      {R0,PC}        
          CFI EndBlock cfiBlock2

        SECTION `.text`:CODE:NOROOT(1)
          CFI Block cfiBlock3 Using cfiCommon0
          CFI Function release
        THUMB


release:
        PUSH     {R4,LR}        
          CFI R14 Frame(CFA, -4)
          CFI R4 Frame(CFA, -8)
          CFI CFA R13+8

        LDR.N    R4,??DataTable5
        LDR      R0,[R4, #+0]   
        CMP      R0,#+1         
        BNE.N    ??release_0    
        LDR.N    R1,??DataTable5_3
        LDR      R0,[R1, #+0]   
        CMP      R0,#+0         
        BEQ.N    ??release_0    

        MOVS     R2,#+0         
        LDR.N    R0,??DataTable5_1
        STR      R2,[R0, #+0]   

        MOVS     R0,#+0         
        STR      R0,[R1, #+0]   

        LDR.N    R0,??DataTable5_4
        LDR      R0,[R0, #+0]   
        CMP      R0,#+0         
        BEQ.N    ??release_0    

        MOVS     R1,#+1         
        LDR.N    R0,??DataTable5_2
        STR      R1,[R0, #+0]   

          CFI FunCall philR_permit
        BL       philR_permit   


??release_0:
        LDR      R0,[R4, #+0]   
        CMP      R0,#+2         
        BNE.N    ??release_1    
        LDR.N    R1,??DataTable5_2
        LDR      R0,[R1, #+0]   
        CMP      R0,#+0         
        BEQ.N    ??release_1    

        MOVS     R0,#+0         
        STR      R0,[R1, #+0]   

        MOVS     R1,#+0         
        LDR.N    R0,??DataTable5_4
        STR      R1,[R0, #+0]   

        LDR.N    R0,??DataTable5_1
        LDR      R0,[R0, #+0]   
        CMP      R0,#+0         
        BEQ.N    ??release_1    

        MOVS     R1,#+1         
        LDR.N    R0,??DataTable5_3
        STR      R1,[R0, #+0]   

          CFI FunCall philL_permit
        BL       philL_permit   


??release_1:
        POP      {R4,PC}        
          CFI EndBlock cfiBlock3

        SECTION `.text`:CODE:NOROOT(1)
          CFI Block cfiBlock4 Using cfiCommon0
          CFI Function main
