class ASTVisualizer:
    def __init__(self):
        self.count = 0
        self.dot_lines = []

    def visualize(self, node):
        self.dot_lines = ["digraph AST {"]
        self.visit(node)
        self.dot_lines.append("}")
        return "\n".join(self.dot_lines)

    def visit(self, node):
        node_id = self.count
        self.count += 1
        
        label = type(node).__name__
        # Add details
        if hasattr(node, 'name'):
            label += f"\\n{node.name}"
        if hasattr(node, 'value'):
            label += f"\\n{node.value}"
        if hasattr(node, 'op'):
            label += f"\\n{node.op}"
        if hasattr(node, 'type_name'):
             label += f"\\n{node.type_name}"

        self.dot_lines.append(f'  node{node_id} [label="{label}"];')

        # Visit children
        children = []
        if hasattr(node, 'declarations'): children.extend(node.declarations)
        if hasattr(node, 'statements'): children.extend(node.statements)
        if hasattr(node, 'params'): children.extend(node.params)
        
        # Single children
        if hasattr(node, 'body') and node.body: children.append(node.body)
        if hasattr(node, 'expression') and node.expression: children.append(node.expression)
        if hasattr(node, 'initializer') and node.initializer: children.append(node.initializer)
        if hasattr(node, 'condition') and node.condition: children.append(node.condition)
        if hasattr(node, 'then_branch') and node.then_branch: children.append(node.then_branch)
        if hasattr(node, 'else_branch') and node.else_branch: children.append(node.else_branch)
        if hasattr(node, 'left') and node.left: children.append(node.left)
        if hasattr(node, 'right') and node.right: children.append(node.right)
        if hasattr(node, 'operand') and node.operand: children.append(node.operand)
        if hasattr(node, 'value') and hasattr(node, 'name'): # Assignment value
            if not isinstance(node.value, (int, float, str)):
                 children.append(node.value)
        if hasattr(node, 'args'): children.extend(node.args)

        for child in children:
            child_id = self.visit(child)
            self.dot_lines.append(f'  node{node_id} -> node{child_id};')
        
        return node_id
