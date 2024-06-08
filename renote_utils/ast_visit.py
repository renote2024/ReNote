import ast
import builtins


class ASTNodeVisitor:
    # Get the names of built-in functions from the builtins module
    builtins_names = set(dir(builtins))

    def __init__(self):
        self.def_list = {}  # {scope : [vars ...]}
        self.use_list = {}

    def visit_node(self, node, scope):
        if not self.def_list.get(scope):
            self.def_list[scope] = []
        if not self.use_list.get(scope):
            self.use_list[scope] = []

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom):
                self.def_list[scope].append(node.module)
            for alias in node.names:
                if alias.asname:
                    self.def_list[scope].append(alias.asname)
                self.def_list[scope].append(alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.def_list[scope].append(node.name)
            for arg in node.args.args:
                self.def_list[scope].append(arg.arg)
            if hasattr(node.args, 'kwarg') and node.args.kwarg is not None:
                self.def_list[scope].append(node.args.kwarg.arg)
            scope += 1
        elif isinstance(node, ast.Lambda):
            for arg in node.args.args:
                self.def_list[scope].append(arg.arg)
            scope += 1
        elif isinstance (node, ast.ClassDef):
            self.def_list[scope].append(node.name)
            scope += 1
        # elif isinstance(node, ast.Name):
        #     if isinstance(node.ctx, ast.Store):
        #         self.def_list[scope].append(node.id)
        #     elif isinstance(node.ctx, ast.Load):
        #         if node.id not in self.builtins_names:
        #             self.use_list[scope].append(node.id)
        #     elif isinstance (node.ctx, ast.Del):
        #         self.def_list[scope].remove(node.id)
        return scope
    

    def visit_children(self, node, scope):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                self.def_list[scope].append(node.id)
            elif isinstance(node.ctx, (ast.Load, ast.Del)):
                if node.id not in self.builtins_names:
                    self.use_list[scope].append(node.id)
        else:
            for child in ast.iter_child_nodes(node):
                child_scope = self.visit_node(child, scope)
                self.visit(child, child_scope)
    

    def visit(self, node, scope):
        if isinstance(node, ast.For):
            self.visit_children(node.target, scope)
            self.visit_children(node.iter, scope)
            for n in node.body:
                self.visit_children(n, scope + 1)
        elif isinstance(node, ast.While):
            self.visit_children(node.test, scope)
            for n in node.body:
                self.visit_children(n, scope + 1)
        else:
            self.visit_children(node, scope)