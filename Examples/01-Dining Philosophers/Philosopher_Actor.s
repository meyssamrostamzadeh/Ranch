


sender:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

eating:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

fL:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

fR:
        DS8 4

        SECTION `.bss`:DATA:REORDER:NOROOT(2)
        DATA

buff:
        DS8 12
		
		
arrive:
        PUSH     {R7,LR}        
          CFI R14 Frame(CFA, -4)
          CFI CFA R13+8

          CFI FunCall forkL_request
        BL       forkL_request  

        POP      {R0,PC}        
          CFI EndBlock cfiBlock0

        SECTION `.text`:CODE:NOROOT(1)
          CFI Block cfiBlock1 Using cfiCommon0
          CFI Function forkL_request
          CFI NoCalls

permit:
        PUSH     {R7,LR}        
          CFI R14 Frame(CFA, -4)
          CFI CFA R13+8

        LDR.N    R0,??DataTable6
        LDR      R0,[R0, #+0]   
        CMP      R0,#+1         
        BNE.N    ??permit_0     

        LDR.N    R1,??DataTable6_1
        LDR      R0,[R1, #+0]   
        CMP      R0,#+0         
        BNE.N    ??permit_1     

        MOVS     R0,#+1         
        STR      R0,[R1, #+0]   

          CFI FunCall forkR_request
        BL       forkR_request  
        B.N      ??permit_1     


??permit_0:
        LDR.N    R0,??DataTable6_1
        LDR      R0,[R0, #+0]   
        CMP      R0,#+0         
        BEQ.N    ??permit_1     
        LDR.N    R1,??DataTable6_2
        LDR      R0,[R1, #+0]   
        CMP      R0,#+0         
        BNE.N    ??permit_1     

        MOVS     R0,#+1         
        STR      R0,[R1, #+0]   

          CFI FunCall eat
        BL       eat            

??permit_1:
        POP      {R0,PC}        
          CFI EndBlock cfiBlock5

        SECTION `.text`:CODE:NOROOT(1)
          CFI Block cfiBlock6 Using cfiCommon0
          CFI Function eat

eat:
        PUSH     {R7,LR}        
          CFI R14 Frame(CFA, -4)
          CFI CFA R13+8

        MOVS     R1,#+1         
        LDR.N    R0,??DataTable6_3
        STR      R1,[R0, #+0]   

          CFI FunCall leave
        BL       leave          

        POP      {R0,PC}        
          CFI EndBlock cfiBlock6

        SECTION `.text`:CODE:NOROOT(1)
          CFI Block cfiBlock7 Using cfiCommon0
          CFI Function leave

leave:
        PUSH     {R7,LR}        
          CFI R14 Frame(CFA, -4)
          CFI CFA R13+8

        MOVS     R1,#+0         
        LDR.N    R0,??DataTable6_1
        STR      R1,[R0, #+0]   

        MOVS     R1,#+0         
        LDR.N    R0,??DataTable6_2
        STR      R1,[R0, #+0]   

        MOVS     R1,#+0         
        LDR.N    R0,??DataTable6_3
        STR      R1,[R0, #+0]   

          CFI FunCall forkL_release
        BL       forkL_release  

          CFI FunCall forkR_release
        BL       forkR_release  

          CFI FunCall arrive
        BL       arrive         

        POP      {R0,PC}        
          CFI EndBlock cfiBlock7


        SECTION `.text`:CODE:NOROOT(1)
          CFI Block cfiBlock8 Using cfiCommon0
          CFI Function main
      
	  