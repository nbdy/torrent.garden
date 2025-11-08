from reflex.vars import var_operation, NumberVar, var_operation_return, StringVar, ArrayVar, BooleanVar
import reflex as rx


@var_operation
def pretty_size(size: NumberVar):
    return var_operation_return(
        js_expression=(
            "((size) => {"
            "const u=['B','KB','MB','GB','TB','PB','EB','ZB','YB'];"
            "let i=0;"
            "while(size>=1024 && i < u.length - 1) size /= 1024, i++;"
            "return`${size.toFixed(2)} ${u[i]}`;"
            "})"
            f"({size})"
        ),
        var_type=StringVar
    )


@var_operation
def pretty_count(count: NumberVar):
    return var_operation_return(
        js_expression=(
            "((count) => {"
            "const u=['','K','M','B','T','P','E','Z','Y'];"
            "let i=0;"
            "while(count>=1000 && i < u.length - 1) count /= 1000, i++;"
            "return `${count.toFixed(2)} ${u[i]}`;"
            "})"
            f"({count})"
        )
    )


@var_operation
def array_count(array: ArrayVar):
    return var_operation_return(
        js_expression=f"({array}).length",
        var_type=NumberVar
    )


@var_operation
def in_array(array: ArrayVar, item):
    return var_operation_return(
        js_expression=f"({array}).includes({item})",
        var_type=BooleanVar
    )



def pie_label_formatter_count():
    return rx.Var.create("({ name, value }) => { const u=['','K','M','B','T','P','E','Z','Y']; let i=0; let c=value; while (c>=1000 && i<u.length-1) { c/=1000; i++; } return `${name}: ${c.toFixed(2)} ${u[i]}`; }")


def pie_tooltip_formatter_count():
    return rx.Var.create("(value, name) => { const u=['','K','M','B','T','P','E','Z','Y']; let i=0; let c=value; while (c>=1000 && i<u.length-1) { c/=1000; i++; } const baseName = (typeof name === 'string' ? name.split(':')[0] : name); return [`${c.toFixed(2)} ${u[i]}`, String(baseName).trim()]; }")


def pie_label_formatter_size():
    return rx.Var.create("({ name, value }) => { const u=['B','KB','MB','GB','TB','PB','EB','ZB','YB']; let i=0; let s=value; while (s>=1024 && i<u.length-1) { s/=1024; i++; } return `${name}: ${s.toFixed(2)} ${u[i]}`; }")


def pie_tooltip_formatter_size():
    return rx.Var.create("(value, name) => { const u=['B','KB','MB','GB','TB','PB','EB','ZB','YB']; let i=0; let s=value; while (s>=1024 && i<u.length-1) { s/=1024; i++; } const baseName = (typeof name === 'string' ? name.split(':')[0] : name); return [`${s.toFixed(2)} ${u[i]}`, String(baseName).trim()]; }")
