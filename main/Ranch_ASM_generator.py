class AssemblyContext:
    def __init__(self):
        self.free_registers = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7']
        self.used_labels = set()

    def get_free_register(self):
        if not self.free_registers:
            raise RuntimeError("No free registers available")
        reg = self.free_registers.pop(0)
        return reg

    def release_register(self, register):
        if register not in self.free_registers:
            self.free_registers.append(register)  # Add back the register when it's freed

    def get_label(self, base_name):
        count = 0
        label = f"{base_name}_{count}"
        while label in self.used_labels:
            count += 1
            label = f"{base_name}_{count}"
        self.used_labels.add(label)
        return label

    def register_var(self, var_name):
        # Could map var names to a memory address or handle global declaration
        pass
