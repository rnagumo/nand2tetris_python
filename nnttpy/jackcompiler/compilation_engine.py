
class CompilationEngine:
    """Compile engine."""

    def __init__(self):
        pass

    def compile_class(self):
        raise NotImplementedError

    def compile_class_var_doc(self):
        raise NotImplementedError

    def compile_subroutine(self):
        raise NotImplementedError

    def compile_parameter_list(self):
        raise NotImplementedError

    def compile_var_dec(self):
        raise NotImplementedError

    def compile_statements(self):
        raise NotImplementedError

    def compile_do(self):
        raise NotImplementedError

    def compile_let(self):
        raise NotImplementedError

    def compile_while(self):
        raise NotImplementedError

    def compile_return(self):
        raise NotImplementedError

    def compile_if(self):
        raise NotImplementedError

    def compile_expression(self):
        raise NotImplementedError

    def compile_term(self):
        raise NotImplementedError

    def compile_expression_list(self):
        raise NotImplementedError
