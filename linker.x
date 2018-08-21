MEMORY
{
    f00d_priv : ORIGIN = 0x40000, LENGTH = 0x4000
}

SECTIONS
{
    .text : { *(.text.start) *(.text) } > f00d_priv
    .rodata : { *(.rodata) } > f00d_priv
    .data : { *(.data*) } > f00d_priv
    .bss : { *(.bss*) } > f00d_priv
}
