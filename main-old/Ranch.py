from Ranch_tokenizer import R_tokenizer
from Ranch_parser3 import R_parser
from Ranch_ASM_generator import AssemblyContext
from Ranch_parser3 import *

def save_tokens_to_file(tokens, filename):
    with open(filename, 'w') as file:
        for token in tokens:
            file.write(f'{token}\n')

# def print_ast(node, indent=0, file=None):
#     spacing = " " * indent
#     if isinstance(node, dict):
#         for key, value in node.items():
#             line = f"{spacing}{key}:"
#             print(line)
#             if file:
#                 file.write(line + '\n')
#             print_ast(value, indent + 4, file)
#     elif isinstance(node, list):
#         for item in node:
#             if isinstance(item, tuple):
#                 if len(item) == 2:  # Handles tuples with 2 elements (e.g., 'else', body)
#                     line = f"{spacing}- {item[0]}:"
#                     print(line)
#                     if file:
#                         file.write(line + '\n')
#                     print_ast(item[1], indent + 4, file)
#                 elif len(item) == 3:  # Handles conditionals like ('if', condition, body)
#                     line = f"{spacing}- {item[0]} ({item[1]}):"
#                     print(line)
#                     if file:
#                         file.write(line + '\n')
#                     print_ast(item[2], indent + 4, file)
#             else:
#                 print_ast(item, indent + 4, file)
#     elif isinstance(node, tuple):
#         line = f"{spacing}({node[0]})"
#         print(line)
#         if file:
#             file.write(line + '\n')
#     else:
#         print(f"{spacing}{node}")
#         if file:
#             file.write(f"{spacing}{node}\n")
  
# def print_ast(node, indent=0, file=None):
#     spacing = " " * indent
    
#     # Handling custom AST node objects
#     if hasattr(node, "__dict__"):  # This checks if the object has attributes (like a class instance)
#         node_type = type(node).__name__
#         line = f"{spacing}{node_type}:"
#         print(line)
#         if file:
#             file.write(line + '\n')

#         # Recursively print each attribute of the node
#         for key, value in node.__dict__.items():
#             line = f"{spacing}  {key}:"
#             print(line)
#             if file:
#                 file.write(line + '\n')
#             print_ast(value, indent + 4, file)
    
#     # Handling dicts, lists, and tuples
#     elif isinstance(node, dict):
#         for key, value in node.items():
#             line = f"{spacing}{key}:"
#             print(line)
#             if file:
#                 file.write(line + '\n')
#             print_ast(value, indent + 4, file)

#     elif isinstance(node, list):
#         for item in node:
#             print_ast(item, indent + 4, file)

#     elif isinstance(node, tuple):
#         line = f"{spacing}({node[0]})"
#         print(line)
#         if file:
#             file.write(line + '\n')

#     else:
#         # If the node is a basic type (str, int, etc.)
#         line = f"{spacing}{node}"
#         print(line)
#         if file:
#             file.write(line + '\n')

# def print_ast(node, indent=0, file=None):
#     spacing = " " * indent
#     if isinstance(node, dict):
#         for key, value in node.items():
#             line = f"{spacing}{key}:"
#             print(line)
#             if file:
#                 file.write(line + '\n')
#             print_ast(value, indent + 4, file)
#     elif isinstance(node, list):
#         for item in node:
#             print_ast(item, indent, file)
#     elif isinstance(node, tuple):
#         line = f"{spacing}({node[0]})"
#         print(line)
#         if file:
#             file.write(line + '\n')
#         for item in node[1:]:
#             print_ast(item, indent + 4, file)
#     elif isinstance(node, Node):  # Check if it's a Node subclass
#         line = str(node)  # Use the __str__ method for pretty printing
#         print(f"{spacing}{line}")
#         if file:
#             file.write(spacing + line + '\n')
#     else:
#         line = f"{spacing}{node}"
#         print(line)
#         if file:
#             file.write(line + '\n')


def print_ast(node, indent=0, file=None):
    """Recursively prints the AST with indentation."""
    if isinstance(node, AssignmentNode):
        print(f"{' ' * indent}Assignment: {node.var_name} = {node.expr}", file=file)
    elif isinstance(node, FunctionCallNode):
        print(f"{' ' * indent}Function Call: {node.function_name}", file=file)
    elif isinstance(node, UnaryOperationNode):
        print(f"{' ' * indent}Unary Operation: {node.operator} {node.operand}", file=file)
        print_ast(node.operand, indent + 2, file)
    elif isinstance(node, BinaryOperationNode):
        print(f"{' ' * indent}Binary Operation: {node.operator}", file=file)
        print_ast(node.left, indent + 2, file)
        print_ast(node.right, indent + 2, file)
    elif isinstance(node, LiteralNode):
        print(f"{' ' * indent}Literal: {node.value}", file=file)
    elif isinstance(node, VariableNode):
        print(f"{' ' * indent}Variable: {node.name}", file=file)
    elif isinstance(node, IfElseNode):
        print(f"{' ' * indent}If-Else Statement:", file=file)
        print_ast(node.condition, indent + 2, file)
        print(f"{' ' * indent}True Body:", file=file)
        for stmt in node.true_body:
            print_ast(stmt, indent + 2, file)
        if node.false_body:
            print(f"{' ' * indent}False Body:", file=file)
            for stmt in node.false_body:
                print_ast(stmt, indent + 2, file)
    elif isinstance(node, ClassNode):
        print(f"{' ' * indent}Class: {node.class_name}", file=file)
        print(f"{' ' * indent}Parameters: {node.params}", file=file)
        print(f"{' ' * indent}Known Rebecs: {node.known_rebecs}", file=file)
        print(f"{' ' * indent}State Variables: {node.state_vars}", file=file)
        print(f"{' ' * indent}Message Servers:", file=file)
        for msg_name, body in node.msg_srvs.items():
            print(f"{' ' * indent}  MsgSrv: {msg_name}", file=file)
            for stmt in body:
                print_ast(stmt, indent + 4, file)
    else:
        print(f"{' ' * indent}Unknown Node: {node}", file=file)





with open('test.rebeca', 'r') as file:
    rebeca_code = file.read()
# print(rebeca_code)
tokens = R_tokenizer(rebeca_code)
save_tokens_to_file(tokens, 'tokens.txt')
# for token in tokens:
#     print(token)

# for parser3
parser = R_parser(tokens)
ast = parser.parse()

with open('ast_output.txt', 'w') as f:
    print_ast(ast, file=f)

context = AssemblyContext()
print(ast.generate_code(context))  # Directly call generate_code on the ClassNode

# for node in ast:
#     print(node.generate_code(context))


# for parser2
  
# parser = R_parser(tokens)
# classes = parser.parse()
# with open('ast_output.txt', 'w') as f:
#     print_ast(classes, file=f)






