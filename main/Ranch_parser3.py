class Node:
    def generate_code(self, context):
        raise NotImplementedError("Subclasses should implement this method")

class AssignmentNode(Node):
    def __init__(self, var_name, expr):
        self.var_name = var_name
        self.expr = expr
    def generate_code(self, context):
        reg = context.get_free_register()
        expr_code = self.expr.generate_code(context)
        return f"{expr_code}\nstr {reg}, =global_{self.var_name}"
    def __str__(self):
        return f"AssignmentNode(var_name={self.var_name}, expr={self.expr})"

class FunctionCallNode(Node):
    def __init__(self, function_name):
        self.function_name = function_name
    def generate_code(self, context):
        return f"bl {self.function_name}"
    def __str__(self):
        return f"FunctionCallNode(function_name={self.function_name})"

class ExpressionNode:
    pass

class UnaryOperationNode(ExpressionNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand
    def __str__(self):
        return f"UnaryOperationNode(operator={self.operator}, operand={self.operand})"

    def generate_code(self, context):
        reg_operand = context.get_free_register()

        # Generate code for the operand
        operand_code = self.operand.generate_code(context)

        if self.operator == '!':
            # Load the operand into a register
            code = f"{operand_code}\ncmp {reg_operand}, #0\n"
            
            # If the operand is 0, the result is 1; otherwise, it is 0
            result_label = context.get_label("false_result")
            done_label = context.get_label("done")

            code += f"beq {result_label}\n"    # If operand == 0, branch to false result
            code += f"mov {reg_operand}, #0\n" # Operand is non-zero, so result is 0
            code += f"b {done_label}\n"
            code += f"{result_label}:\n"
            code += f"mov {reg_operand}, #1\n" # Operand is 0, so result is 1
            code += f"{done_label}:\n"

            # Release the register after the result is computed
            context.release_register(reg_operand)

            return code
        else:
            raise NotImplementedError(f"Unary operator {self.operator} not supported")

class BinaryOperationNode(ExpressionNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def __str__(self):
        return f"BinaryOperationNode(left={self.left}, operator={self.operator}, right={self.right})"

    def generate_code(self, context):
        reg_left = context.get_free_register()
        label_end = context.get_label('end')

        left_code = self.left.generate_code(context)

        if self.operator == '&&':
            # Short-circuit logic for AND
            label_false = context.get_label('false')
            code = f"{left_code}\n"
            code += f"cmp {reg_left}, #0\n"  # Compare left to 0
            code += f"beq {label_false}\n"  # Branch to false if left is 0

            # Evaluate right
            reg_right = context.get_free_register()
            right_code = self.right.generate_code(context)
            code += f"{right_code}\n"
            code += f"cmp {reg_right}, #0\n"  # Compare right to 0
            code += f"beq {label_false}\n"  # Branch to false if right is 0

            # Both are true, set result to true
            code += f"mov {reg_left}, #1\n"  # Set result to true
            code += f"b {label_end}\n"

            # False label: set result to false
            code += f"{label_false}:\n"
            code += f"mov {reg_left}, #0\n"

        elif self.operator == '||':
            # Short-circuit logic for OR
            label_true = context.get_label('true')
            code = f"{left_code}\n"
            code += f"cmp {reg_left}, #0\n"  # Compare left to 0
            code += f"bne {label_true}\n"  # Branch to true if left is not 0

            # Evaluate right
            reg_right = context.get_free_register()
            right_code = self.right.generate_code(context)
            code += f"{right_code}\n"
            code += f"cmp {reg_right}, #0\n"  # Compare right to 0
            code += f"bne {label_true}\n"  # Branch to true if right is not 0

            # Both are false, set result to false
            code += f"mov {reg_left}, #0\n"
            code += f"b {label_end}\n"

            # True label: set result to true
            code += f"{label_true}:\n"
            code += f"mov {reg_left}, #1\n"

        # Final label (end of AND/OR operation)
        code += f"{label_end}:\n"

        context.release_register(reg_right)
        return code

class LiteralNode(ExpressionNode):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return f"LiteralNode(value={self.value})"
    def generate_code(self, context):
        reg = context.get_free_register()
        return f"ldr {reg}, ={self.value}"

class IfElseNode(Node):
    def __init__(self, condition, true_body, false_body=None):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body
    def __str__(self):
        return f"IfElseNode(condition={self.condition}, true_body={self.true_body}, false_body={self.false_body})"
    def generate_code(self, context):
        true_label = context.get_label("true")
        end_label = context.get_label("end")

        # Generate code for the condition
        condition_code = self.condition.generate_code(context)

        # Use cmp instruction, not test
        code = f"{condition_code}\ncmp r0, #0\nbeq {end_label}\n"

        # Generate code for the true body
        true_body_code = "\n".join(node.generate_code(context) for node in self.true_body)
        code += f"{true_label}:\n{true_body_code}\n"

        if self.false_body:
            false_body_code = "\n".join(node.generate_code(context) for node in self.false_body)
            code += f"b {end_label}\n{false_body_code}\n"

        code += f"{end_label}:\n"

        return code

class VariableNode(ExpressionNode):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"VariableNode(name={self.name})"
    def generate_code(self, context):
        reg = context.get_free_register()
        return f"ldr {reg}, [{self.name}]"

class ClassNode(Node):
    def __init__(self, class_name, params, known_rebecs, state_vars, msg_srvs):
        self.class_name = class_name
        self.params = params
        self.known_rebecs = known_rebecs
        self.state_vars = state_vars
        self.msg_srvs = msg_srvs
    def __str__(self):
        msg_srvs_str = {msg_name: [str(stmt) for stmt in body] for msg_name, body in self.msg_srvs.items()}
        return (f"ClassNode(class_name={self.class_name}, "
                f"params={self.params}, known_rebecs={self.known_rebecs}, "
                f"state_vars={self.state_vars}, msg_srvs={msg_srvs_str})")
    def generate_code(self, context):
        code = f"; Class: {self.class_name}\n"

        # Handle state variables
        code += "; State variables:\n"
        for var_name, var_type in self.state_vars.items():
            code += f"ldr r0, ={var_name}\n"  # Load the state variable
            # You can add handling here depending on the var_type

        # Handle known rebecs
        code += "; Known rebecs:\n"
        for rebec_type, rebec_name in self.known_rebecs.items():
            code += f"ldr r1, ={rebec_name}\n"

        # Generate code for each message server
        code += "; Message servers:\n"
        for msg_name, body in self.msg_srvs.items():
            code += f"; MsgSrv: {msg_name}\n"
            for stmt in body:
                code += stmt.generate_code(context) + "\n"

        return code

class R_parser:
    def __init__(self, tokens):
        self.recent_tokens = []  # To store the last processed tokens
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.parse_class()

    def parse_class(self):
        self.expect('ID', 'reactiveclass')  # Expect the 'reactiveclass' keyword
        class_name = self.expect('ID')  # Expect the class name (e.g., Philosopher)
        self.expect('PUNCT', '(')
        param = self.expect('NUMBER')  # Expect a number inside parentheses for the parameter
        self.expect('PUNCT', ')')
        self.expect('PUNCT', '{')

        known_rebecs = self.parse_known_rebecs()
        state_vars = self.parse_state_vars()
         # Initialize msg_srvs as an empty dictionary
        msg_srvs = {}
        
        # Parse message servers
        while self.check('ID', 'msgsrv') or self.check('PUNCT', '}'):
            if self.check('ID', 'msgsrv'):
                msg_srvs.update(self.parse_msg_srvs())
            else:
                break  # Exit loop if we encounter a closing brace

        self.expect('PUNCT', '}')  # End of the class definition

        return ClassNode(class_name, param, known_rebecs, state_vars, msg_srvs)

    def parse_known_rebecs(self):
        known_rebecs = {}
        self.expect('ID', 'knownrebecs')
        self.expect('PUNCT', '{')
        while not self.check('PUNCT', '}'):
            rebec_type = self.expect('ID')  # e.g., Fork
            rebec_name = self.expect('ID')  # e.g., fork
            self.expect('PUNCT', ';')  # Expect the semicolon to end this entry
            known_rebecs[rebec_type] = rebec_name  # Store the pair in the dictionary
        self.expect('PUNCT', '}')  # End of known rebecs section
        return known_rebecs

    def parse_state_vars(self):
        state_vars = {}
        self.expect('ID', 'statevars')
        self.expect('PUNCT', '{')
        while not self.check('PUNCT', '}'):
            var_type = self.expect('ID')  # e.g., boolean
            var_name = self.expect('ID')  # e.g., eating
            self.expect('PUNCT', ';')  # Expect the semicolon to end this entry
            state_vars[var_name] = var_type  # Store the variable type with its name
        self.expect('PUNCT', '}')
        return state_vars

    def parse_msg_srvs(self):
        msg_srvs = {}
        self.expect('ID', 'msgsrv')  # Expect the 'msgsrv' keyword
        msg_name = self.expect('ID')  # e.g., initial
        self.expect('PUNCT', '(')  # Expect the opening parenthesis
        self.expect('PUNCT', ')')  # Expect the closing parenthesis (no arguments in this case)
        self.expect('PUNCT', '{')  # Expect the colon after the message name
        body = self.parse_body()  # Parse the body of the message server
        msg_srvs[msg_name] = body

        self.expect('PUNCT', '}')  # End of the message server

        return msg_srvs

    def parse_body(self):
        # This is a placeholder for parsing message server bodies, like assignments and if-else statements
        body = []
        while not self.check('PUNCT', '}'):
            if self.check('ID', 'if'):
                body.append(self.parse_if_statement())
            else:
                body.append(self.parse_statement())
        return body

    def parse_method_call(self, var_name):
        self.expect('DOT')  # Consume the dot
        method_name = self.expect('ID')  # Expect the method name (e.g., arrive)
        self.expect('PUNCT', '(')  # Skip '('
        self.expect('PUNCT', ')')  # Expect the closing parenthesis
        self.expect('PUNCT', ';')  # Expect the closing semicolon
        return FunctionCallNode(function_name=f"{var_name}.{method_name}")

    def parse_statement(self):
        var_name = self.expect('ID')

        # Check for method call (e.g., self.arrive())
        if self.check('DOT'):
            return self.parse_method_call(var_name)

        # Check for function call (e.g., self.arrive())
        if self.check('PUNCT', '('):
            return self.parse_function_call(var_name)

        # Otherwise, treat it as an assignment
        elif self.check('OP', '='):
            return self.parse_assignment(var_name)

        else:
            self.error(f"Expected '(' for function call or '=' for assignment, found {self.tokens[self.pos]}")

    def parse_assignment(self, var_name):
        self.expect('OP', '=')  # Expect '='
        expr = self.parse_expression()  # Parse the right-hand side expression
        self.expect('PUNCT', ';')  # Expect the closing semicolon
        return AssignmentNode(var_name, expr)

    def parse_function_call(self, function_name):
        self.expect('PUNCT', '(')  # Skip '('
        self.expect('PUNCT', ')')  # Function calls do not have arguments in this case
        self.expect('PUNCT', ';')  # Expect the closing semicolon
        return FunctionCallNode(function_name)

    def parse_if_statement(self):
        self.expect('ID', 'if')
        self.expect('PUNCT', '(')
        condition = self.parse_expression()
        self.expect('PUNCT', ')')
        self.expect('PUNCT', '{')
        true_body = self.parse_body()
        self.expect('PUNCT', '}')
        false_body = None
        if self.check('ID', 'else'):
            self.expect('ID', 'else')
            self.expect('PUNCT', '{')
            false_body = self.parse_body()
            self.expect('PUNCT', '}')
        return IfElseNode(condition, true_body, false_body)

    def parse_expression(self):
        token = self.tokens[self.pos]
        # Handle unary operators
        if token[0] == 'OP' and token[1] == '!':
            self.pos += 1
            operand = self.parse_expression()  # Parse the operand after unary operator
            return UnaryOperationNode(operator='!', operand=operand)
        
        # Parse primary expression (variables or literals)
        if token[0] == 'ID':
            self.pos += 1
            return VariableNode(name=token[1])
        elif token[0] == 'NUMBER':
            self.pos += 1
            return LiteralNode(value=token[1])

        # Handle binary expressions
        left = self.parse_primary_expression()  # Primary expression parsing first
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'OP':
            operator = self.tokens[self.pos][1]
            self.pos += 1
            right = self.parse_primary_expression()
            left = BinaryOperationNode(left=left, operator=operator, right=right)

        return left

    def expect(self, token_type, value=None):
        token = self.tokens[self.pos]
        if token[0] != token_type or (value and token[1] != value):
            self.error(f"Expected {value}, found {token}")

        # Track recent tokens (limit to 10)
        self.recent_tokens.append(token)
        if len(self.recent_tokens) > 10:
            self.recent_tokens.pop(0)

        self.pos += 1
        return token[1]

    def check(self, token_type, value=None):
        if self.pos >= len(self.tokens):
            return False
        token = self.tokens[self.pos]
        return token[0] == token_type and (value is None or token[1] == value)

    def error(self, message):
        recent_tokens_str = ', '.join([str(token) for token in self.recent_tokens])
        raise RuntimeError(f"{message}\nLast 10 tokens: {recent_tokens_str}")
