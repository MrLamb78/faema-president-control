#!/usr/bin/env python3
"""
gen_sch.py — Gera o esquemático KiCad Rev.5 para Faema President.

Lê lib_symbols do arquivo existente e gera um novo .kicad_sch completo
com todos os componentes novos e atualizados.

Uso:
    python3 kicad/gen_sch.py
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_SCH  = os.path.join(SCRIPT_DIR, "faema-president.kicad_sch")
OUTPUT_SCH = os.path.join(SCRIPT_DIR, "faema-president.kicad_sch")

# ---------------------------------------------------------------------------
# UUID helpers
# ---------------------------------------------------------------------------
def sym_uuid(n):
    """Symbol instance UUID: b{n:07x}0-0001-4000-8000-000000000001"""
    return f"b{n:07x}0-0001-4000-8000-000000000001"

def pin_uuid(n, p):
    """Pin UUID within instance n, pin p: c{n:07x}0-0001-4000-8000-{p:012x}"""
    return f"c{n:07x}0-0001-4000-8000-{p:012x}"

def lbl_uuid(n):
    """Global label UUID: d{n:07x}0-0001-4000-8000-000000000001"""
    return f"d{n:07x}0-0001-4000-8000-000000000001"

def pwr_uuid(n):
    """Power symbol UUID: e{n:07x}0-0001-4000-8000-000000000001"""
    return f"e{n:07x}0-0001-4000-8000-000000000001"

def wire_uuid(n):
    """Wire UUID: f{n:07x}0-0001-4000-8000-000000000001"""
    return f"f{n:07x}0-0001-4000-8000-000000000001"

# ---------------------------------------------------------------------------
# Counter state for auto-incrementing IDs
# ---------------------------------------------------------------------------
_sym_n   = 0x100    # start at b0000100
_lbl_n   = 0x200    # start at d0000200
_pwr_n   = 0x100    # start at e0000100
_wire_n  = 0x100    # start at f0000100
_pwr_ref = 100      # #PWR counter

def next_sym():
    global _sym_n; n = _sym_n; _sym_n += 1; return n

def next_lbl():
    global _lbl_n; n = _lbl_n; _lbl_n += 1; return n

def next_pwr():
    global _pwr_n; n = _pwr_n; _pwr_n += 1; return n

def next_wire():
    global _wire_n; n = _wire_n; _wire_n += 1; return n

def next_pwr_ref():
    global _pwr_ref; n = _pwr_ref; _pwr_ref += 1; return n

# ---------------------------------------------------------------------------
# Coordinate rounding
# ---------------------------------------------------------------------------
def r(x):
    return round(float(x), 3)

# ---------------------------------------------------------------------------
# KiCad element builders
# ---------------------------------------------------------------------------

def prop(name, value, at_x, at_y, at_rot=0, hide=False, size=1.27,
         justify=None, show_name="no", do_not_autoplace="no"):
    hide_str = "\n\t\t(hide yes)" if hide else ""
    just_str = f"\n\t\t\t(justify {justify})" if justify else ""
    return (
        f'\t(property "{name}" "{value}"\n'
        f'\t\t(at {r(at_x)} {r(at_y)} {at_rot}){hide_str}\n'
        f'\t\t(show_name {show_name})\n'
        f'\t\t(do_not_autoplace {do_not_autoplace})\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size {size} {size})\n'
        f'\t\t\t)\n'
        f'{just_str}'
        f'\t\t)\n'
        f'\t)'
    )


def sym_instance(lib_id, at_x, at_y, rot, ref, value, uuid_n, pins,
                 footprint="", datasheet="", description="",
                 ref_off_x=None, ref_off_y=None,
                 val_off_x=None, val_off_y=None):
    """
    Generate a (symbol ...) instance block.
    pins: list of pin numbers as strings (e.g. ["1","2"])
    """
    rx, ry = r(at_x), r(at_y)
    # Default label offsets
    if ref_off_x is None: ref_off_x = rx + 2.54
    if ref_off_y is None: ref_off_y = ry - 2.54
    if val_off_x is None: val_off_x = rx - 2.54
    if val_off_y is None: val_off_y = ry + 2.54

    pin_lines = ""
    for i, p in enumerate(pins, 1):
        pin_lines += f'\t(pin "{p}"\n\t\t(uuid "{pin_uuid(uuid_n, int(p) if p.isdigit() else i)}")\n\t)\n'

    fp_hide  = "\n\t\t(hide yes)" if True else ""
    ds_hide  = "\n\t\t(hide yes)" if True else ""

    return (
        f'(symbol\n'
        f'\t(lib_id "{lib_id}")\n'
        f'\t(at {rx} {ry} {rot})\n'
        f'\t(unit 1)\n'
        f'\t(body_style 1)\n'
        f'\t(exclude_from_sim no)\n'
        f'\t(in_bom yes)\n'
        f'\t(on_board yes)\n'
        f'\t(in_pos_files yes)\n'
        f'\t(dnp no)\n'
        f'\t(uuid "{sym_uuid(uuid_n)}")\n'
        f'\t(property "Reference" "{ref}"\n'
        f'\t\t(at {r(ref_off_x)} {r(ref_off_y)} 0)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Value" "{value}"\n'
        f'\t\t(at {r(val_off_x)} {r(val_off_y)} 0)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Footprint" "{footprint}"\n'
        f'\t\t(at {rx} {ry} 0){fp_hide}\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Datasheet" "{datasheet}"\n'
        f'\t\t(at {rx} {ry} 0){ds_hide}\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Description" "{description}"\n'
        f'\t\t(at {rx} {ry} 0)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'{pin_lines}'
        f'\t(instances\n'
        f'\t\t(project "faema-president"\n'
        f'\t\t\t(path "/a0000000-0000-4000-8000-000000000001"\n'
        f'\t\t\t\t(reference "{ref}")\n'
        f'\t\t\t\t(unit 1)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f')\n'
    )


def power_sym(net, at_x, at_y, pwr_n=None, ref_n=None):
    """
    Generate a placed power symbol (GND, +3V3, +5V).
    net: "GND", "+3V3", or "+5V"
    """
    if pwr_n is None:
        pwr_n = next_pwr()
    if ref_n is None:
        ref_n = next_pwr_ref()

    rx, ry = r(at_x), r(at_y)
    val_off_y = ry + 2.54 if net != "GND" else ry - 2.54

    return (
        f'(symbol\n'
        f'\t(lib_id "power:{net}")\n'
        f'\t(at {rx} {ry} 0)\n'
        f'\t(unit 1)\n'
        f'\t(body_style 1)\n'
        f'\t(exclude_from_sim no)\n'
        f'\t(in_bom yes)\n'
        f'\t(on_board yes)\n'
        f'\t(in_pos_files yes)\n'
        f'\t(dnp no)\n'
        f'\t(uuid "{pwr_uuid(pwr_n)}")\n'
        f'\t(property "Reference" "#PWR{ref_n:02d}"\n'
        f'\t\t(at {rx} {ry} 0)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(hide yes)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Value" "{net}"\n'
        f'\t\t(at {rx} {r(val_off_y)} 0)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Footprint" ""\n'
        f'\t\t(at 0 0 0)\n'
        f'\t\t(hide yes)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Datasheet" ""\n'
        f'\t\t(at 0 0 0)\n'
        f'\t\t(hide yes)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(property "Description" ""\n'
        f'\t\t(at 0 0 0)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f'\t(pin "1"\n'
        f'\t\t(uuid "{pwr_uuid(pwr_n)[:8]}-0001-4000-8000-{pwr_n:012x}")\n'
        f'\t)\n'
        f'\t(instances\n'
        f'\t\t(project "faema-president"\n'
        f'\t\t\t(path "/a0000000-0000-4000-8000-000000000001"\n'
        f'\t\t\t\t(reference "#PWR{ref_n:02d}")\n'
        f'\t\t\t\t(unit 1)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f')\n'
    )


def global_label(name, at_x, at_y, rot, shape="input", lbl_n=None):
    """
    Generate a global_label element.
    rot=0 faces right, rot=180 faces left.
    """
    if lbl_n is None:
        lbl_n = next_lbl()
    rx, ry = r(at_x), r(at_y)
    justify = "right" if rot == 180 else "left"
    return (
        f'(global_label "{name}"\n'
        f'\t(shape {shape})\n'
        f'\t(at {rx} {ry} {rot})\n'
        f'\t(effects\n'
        f'\t\t(font\n'
        f'\t\t\t(size 1.27 1.27)\n'
        f'\t\t)\n'
        f'\t\t(justify {justify})\n'
        f'\t)\n'
        f'\t(uuid "{lbl_uuid(lbl_n)}")\n'
        f'\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"\n'
        f'\t\t(at {rx} {ry} {rot})\n'
        f'\t\t(hide yes)\n'
        f'\t\t(show_name no)\n'
        f'\t\t(do_not_autoplace no)\n'
        f'\t\t(effects\n'
        f'\t\t\t(font\n'
        f'\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)\n'
        f')\n'
    )


def wire(x1, y1, x2, y2, wire_n=None):
    if wire_n is None:
        wire_n = next_wire()
    return (
        f'(wire\n'
        f'\t(pts\n'
        f'\t\t(xy {r(x1)} {r(y1)}) (xy {r(x2)} {r(y2)})\n'
        f'\t)\n'
        f'\t(stroke\n'
        f'\t\t(width 0)\n'
        f'\t\t(type default)\n'
        f'\t)\n'
        f'\t(uuid "{wire_uuid(wire_n)}")\n'
        f')\n'
    )


def fanout(name, pin_x, pin_y, side="left", shape="input", dx=7.62):
    """Create a short horizontal wire plus a label for readable pin fanout."""
    if side == "left":
        label_x = pin_x - dx
        rot = 180
    else:
        label_x = pin_x + dx
        rot = 0

    return [
        wire(pin_x, pin_y, label_x, pin_y),
        global_label(name, label_x, pin_y, rot, shape),
    ]


def vertical_tap(name, pin_x, pin_y, direction="up", shape="input", dy=6.35):
    """Create a short vertical wire plus a label for vertical parts like fuses."""
    if direction == "up":
        label_y = pin_y - dy
        rot = 270
    else:
        label_y = pin_y + dy
        rot = 90

    return [
        wire(pin_x, pin_y, pin_x, label_y),
        global_label(name, pin_x, label_y, rot, shape),
    ]


# ---------------------------------------------------------------------------
# New lib_symbol definitions
# ---------------------------------------------------------------------------
NEW_LIB_SYMBOLS = r"""
	(symbol "faema:NMOS_GSD"
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "Q"
			(at 2.54 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "NMOS"
			(at 2.54 -2.54 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(symbol "NMOS_GSD_0_1"
			(polyline
				(pts
					(xy 0 0) (xy -1.27 0) (xy -1.27 -2.54) (xy 0 -2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 0) (xy -1.27 0) (xy -1.27 2.54) (xy 0 2.54)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -1.27 0) (xy -3.81 0)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 -1.27) (xy 0 -3.81)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 1.27) (xy 0 3.81)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -0.508 -2.032) (xy 0 -1.27) (xy 0.508 -2.032)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(rectangle
				(start -1.524 2.921)
				(end 1.524 -2.921)
				(stroke
					(width 0.254)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "NMOS_GSD_1_1"
			(pin input line
				(at -3.81 0 0)
				(length 1.27)
				(name "G"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 0 -3.81 270)
				(length 1.27)
				(name "D"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 0 3.81 90)
				(length 1.27)
				(name "S"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
		(embedded_fonts no)
	)
	(symbol "faema:Fuse"
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "F"
			(at 1.778 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "Fuse"
			(at -1.778 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(symbol "Fuse_0_1"
			(rectangle
				(start -1.016 2.54)
				(end 1.016 -2.54)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 2.54) (xy 0 3.81)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 -2.54) (xy 0 -3.81)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "Fuse_1_1"
			(pin passive line
				(at 0 3.81 270)
				(length 1.27)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 0 -3.81 90)
				(length 1.27)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
		(embedded_fonts no)
	)
	(symbol "faema:MOV"
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "RV"
			(at 1.778 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "MOV"
			(at -1.778 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(symbol "MOV_0_1"
			(rectangle
				(start -1.016 2.54)
				(end 1.016 -2.54)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 2.54) (xy 0 3.81)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy 0 -2.54) (xy 0 -3.81)
				)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type none)
				)
			)
			(polyline
				(pts
					(xy -0.762 1.016) (xy 0 0) (xy 0.762 -1.016)
				)
				(stroke
					(width 0.254)
					(type default)
				)
				(fill
					(type none)
				)
			)
		)
		(symbol "MOV_1_1"
			(pin passive line
				(at 0 3.81 270)
				(length 1.27)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at 0 -3.81 90)
				(length 1.27)
				(name "~"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
		(embedded_fonts no)
	)
	(symbol "faema:Conn_5pin"
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "J"
			(at 0 -7.62 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "Conn_5pin"
			(at 0 7.62 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(symbol "Conn_5pin_0_1"
			(rectangle
				(start -2.54 6.35)
				(end 2.54 -6.35)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type background)
				)
			)
		)
		(symbol "Conn_5pin_1_1"
			(pin passive line
				(at -5.08 5.08 0)
				(length 2.54)
				(name "Pin_1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 2.54 0)
				(length 2.54)
				(name "Pin_2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 0 0)
				(length 2.54)
				(name "Pin_3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -2.54 0)
				(length 2.54)
				(name "Pin_4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -5.08 0)
				(length 2.54)
				(name "Pin_5"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "5"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
		(embedded_fonts no)
	)
	(symbol "faema:Conn_6pin"
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "J"
			(at 0 -8.89 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "Conn_6pin"
			(at 0 8.89 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(symbol "Conn_6pin_0_1"
			(rectangle
				(start -2.54 7.62)
				(end 2.54 -7.62)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type background)
				)
			)
		)
		(symbol "Conn_6pin_1_1"
			(pin passive line
				(at -5.08 6.35 0)
				(length 2.54)
				(name "Pin_1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 3.81 0)
				(length 2.54)
				(name "Pin_2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 1.27 0)
				(length 2.54)
				(name "Pin_3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -1.27 0)
				(length 2.54)
				(name "Pin_4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -3.81 0)
				(length 2.54)
				(name "Pin_5"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "5"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -6.35 0)
				(length 2.54)
				(name "Pin_6"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "6"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
		(embedded_fonts no)
	)
	(symbol "faema:Conn_8pin"
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(duplicate_pin_numbers_are_jumpers no)
		(property "Reference" "J"
			(at 0 -11.43 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "Conn_8pin"
			(at 0 11.43 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(hide yes)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" ""
			(at 0 0 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(symbol "Conn_8pin_0_1"
			(rectangle
				(start -2.54 10.16)
				(end 2.54 -10.16)
				(stroke
					(width 0)
					(type default)
				)
				(fill
					(type background)
				)
			)
		)
		(symbol "Conn_8pin_1_1"
			(pin passive line
				(at -5.08 8.89 0)
				(length 2.54)
				(name "Pin_1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "1"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 6.35 0)
				(length 2.54)
				(name "Pin_2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "2"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 3.81 0)
				(length 2.54)
				(name "Pin_3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "3"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 1.27 0)
				(length 2.54)
				(name "Pin_4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "4"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -1.27 0)
				(length 2.54)
				(name "Pin_5"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "5"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -3.81 0)
				(length 2.54)
				(name "Pin_6"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "6"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -6.35 0)
				(length 2.54)
				(name "Pin_7"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "7"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
			(pin passive line
				(at -5.08 -8.89 0)
				(length 2.54)
				(name "Pin_8"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
				(number "8"
					(effects
						(font
							(size 1.27 1.27)
						)
					)
				)
			)
		)
		(embedded_fonts no)
	)
"""

# ---------------------------------------------------------------------------
# Read & extract lib_symbols from existing file
# ---------------------------------------------------------------------------
def extract_lib_symbols(path):
    """
    Reads the file and extracts the content between (lib_symbols and its
    matching closing parenthesis.  Returns the raw string (without the outer
    `(lib_symbols` / `)` wrapper).
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Find the start of (lib_symbols
    start_kw = "(lib_symbols"
    idx = text.find(start_kw)
    if idx == -1:
        raise ValueError("(lib_symbols not found in input file")

    # Walk forward to find the matching closing paren
    depth = 0
    i = idx
    while i < len(text):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1

    inner = text[idx + len(start_kw):i]   # content between the outer parens
    return inner


# ---------------------------------------------------------------------------
# Build existing component instances (preserve exact UUIDs from Rev.4)
# ---------------------------------------------------------------------------
def make_existing_components():
    """Return the string block with all Rev.4 component instances, updating
    R7 value to 220R."""

    out = []

    # ---- J1 Conn_3pin ----
    out.append(
        "(symbol\n"
        "\t(lib_id \"faema:Conn_3pin\")\n"
        "\t(at 25 45 0)\n"
        "\t(unit 1)\n"
        "\t(body_style 1)\n"
        "\t(exclude_from_sim no)\n"
        "\t(in_bom yes)\n"
        "\t(on_board yes)\n"
        "\t(in_pos_files yes)\n"
        "\t(dnp no)\n"
        "\t(uuid \"b0000001-0001-4000-8000-000000000001\")\n"
        "\t(property \"Reference\" \"J1\"\n"
        "\t\t(at 25 37 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Value\" \"AC_INPUT\"\n"
        "\t\t(at 25 53 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Footprint\" \"\"\n"
        "\t\t(at 25 45 0)\n"
        "\t\t(hide yes)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Datasheet\" \"\"\n"
        "\t\t(at 25 45 0)\n"
        "\t\t(hide yes)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Description\" \"\"\n"
        "\t\t(at 25 45 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(pin \"1\" (uuid \"c0000001-0001-4000-8000-000000000001\"))\n"
        "\t(pin \"2\" (uuid \"c0000001-0001-4000-8000-000000000002\"))\n"
        "\t(pin \"3\" (uuid \"c0000001-0001-4000-8000-000000000003\"))\n"
        "\t(instances\n"
        "\t\t(project \"faema-president\"\n"
        "\t\t\t(path \"/a0000000-0000-4000-8000-000000000001\"\n"
        "\t\t\t\t(reference \"J1\")\n"
        "\t\t\t\t(unit 1)\n"
        "\t\t\t)\n"
        "\t\t)\n"
        "\t)\n"
        ")\n"
    )

    def comp(lib_id, x, y, rot, ref, value, uuid_hex, pins,
             ref_dx=0, ref_dy=-7.62, val_dx=0, val_dy=7.62):
        rx, ry = r(x), r(y)
        pin_lines = ""
        for p in pins:
            pn = p if isinstance(p, int) else int(p) if str(p).isdigit() else 0
            pin_lines += f"\t(pin \"{p}\" (uuid \"c{uuid_hex}0-0001-4000-8000-{pn:012x}\"))\n"
        return (
            f"(symbol\n"
            f"\t(lib_id \"{lib_id}\")\n"
            f"\t(at {rx} {ry} {rot})\n"
            f"\t(unit 1)\n"
            f"\t(body_style 1)\n"
            f"\t(exclude_from_sim no)\n"
            f"\t(in_bom yes)\n"
            f"\t(on_board yes)\n"
            f"\t(in_pos_files yes)\n"
            f"\t(dnp no)\n"
            f"\t(uuid \"b{uuid_hex}0-0001-4000-8000-000000000001\")\n"
            f"\t(property \"Reference\" \"{ref}\"\n"
            f"\t\t(at {r(rx+ref_dx)} {r(ry+ref_dy)} 0)\n"
            f"\t\t(show_name no)\n"
            f"\t\t(do_not_autoplace no)\n"
            f"\t\t(effects (font (size 1.27 1.27)))\n"
            f"\t)\n"
            f"\t(property \"Value\" \"{value}\"\n"
            f"\t\t(at {r(rx+val_dx)} {r(ry+val_dy)} 0)\n"
            f"\t\t(show_name no)\n"
            f"\t\t(do_not_autoplace no)\n"
            f"\t\t(effects (font (size 1.27 1.27)))\n"
            f"\t)\n"
            f"\t(property \"Footprint\" \"\"\n"
            f"\t\t(at {rx} {ry} 0)\n"
            f"\t\t(hide yes)\n"
            f"\t\t(show_name no)\n"
            f"\t\t(do_not_autoplace no)\n"
            f"\t\t(effects (font (size 1.27 1.27)))\n"
            f"\t)\n"
            f"\t(property \"Datasheet\" \"\"\n"
            f"\t\t(at {rx} {ry} 0)\n"
            f"\t\t(hide yes)\n"
            f"\t\t(show_name no)\n"
            f"\t\t(do_not_autoplace no)\n"
            f"\t\t(effects (font (size 1.27 1.27)))\n"
            f"\t)\n"
            f"\t(property \"Description\" \"\"\n"
            f"\t\t(at {rx} {ry} 0)\n"
            f"\t\t(show_name no)\n"
            f"\t\t(do_not_autoplace no)\n"
            f"\t\t(effects (font (size 1.27 1.27)))\n"
            f"\t)\n"
            f"{pin_lines}"
            f"\t(instances\n"
            f"\t\t(project \"faema-president\"\n"
            f"\t\t\t(path \"/a0000000-0000-4000-8000-000000000001\"\n"
            f"\t\t\t\t(reference \"{ref}\")\n"
            f"\t\t\t\t(unit 1)\n"
            f"\t\t\t)\n"
            f"\t\t)\n"
            f"\t)\n"
            f")\n"
        )

    # U2 HLK_PM05
    out.append(comp("faema:HLK_PM05", 72, 45, 0, "U2", "HLK-PM05",
                    "0000002", [1,2,3,4],
                    ref_dy=-12.7, val_dy=12.7))

    # SSR1 SSR_40DA
    out.append(comp("faema:SSR_40DA", 80, 86, 0, "SSR1", "SSR-40DA",
                    "0000003", [1,2,3,4],
                    ref_dy=-12.7, val_dy=12.7))

    # J2 Conn_2pin
    out.append(comp("faema:Conn_2pin", 125, 86, 0, "J2", "CALDEIRA_2400W",
                    "0000004", [1,2],
                    ref_dy=-6.35, val_dy=7.62))

    # U3 AMS1117_3V3
    out.append(comp("faema:AMS1117_3V3", 150, 45, 0, "U3", "AMS1117-3.3",
                    "0000005", [1,2,3],
                    ref_dy=-10.16, val_dy=10.16))

    # U1 ESP32_S3_Mini — many pins
    esp_pins = list(range(1, 26))
    esp_pinstr = [str(p) for p in esp_pins]
    out.append(comp("faema:ESP32_S3_Mini", 275, 170, 0, "U1", "ESP32-S3 Mini",
                    "0000006", esp_pinstr,
                    ref_dy=-40, val_dy=38))

    # U4 MAX31865 caldeira
    max_pins_u4 = [str(i) for i in range(1, 14)]
    out.append(comp("faema:MAX31865", 120, 145, 0, "U4", "MAX31865_CALDEIRA",
                    "0000007", max_pins_u4,
                    ref_dy=-23, val_dy=23))

    # U6 MAX31865 grupo
    max_pins_u6 = [str(i) for i in range(1, 14)]
    out.append(comp("faema:MAX31865", 120, 220, 0, "U6", "MAX31865_GRUPO",
                    "0000008", max_pins_u6,
                    ref_dy=-23, val_dy=23))

    # J3 Conn_4pin (PT100 caldeira)
    out.append(comp("faema:Conn_4pin", 60, 145, 0, "J3", "PT100_CALDEIRA",
                    "0000009", [1,2,3,4],
                    ref_dy=-9.19, val_dy=9.86))

    # J6 Conn_4pin (PT100 grupo)
    out.append(comp("faema:Conn_4pin", 60, 220, 0, "J6", "PT100_GRUPO",
                    "0000010", [1,2,3,4],
                    ref_dy=-9.5, val_dy=10))

    # J7 Conn_2pin (sonda nivel)
    out.append(comp("faema:Conn_2pin", 60, 250, 0, "J7", "SONDA_NIVEL",
                    "0000011", [1,2],
                    ref_dy=-6.4, val_dy=6.3))

    # U5 DS3231 — pins 1-5, 14, 15, 16
    def ds_pins_str(uuid_hex, pins_list):
        lines = ""
        for p in pins_list:
            lines += f"\t(pin \"{p}\" (uuid \"c{uuid_hex}0-0001-4000-8000-{int(p):012x}\"))\n"
        return lines

    ds_pins = ["1","2","3","4","5","14","15","16"]
    rx, ry = r(360), r(155)
    out.append(
        f"(symbol\n"
        f"\t(lib_id \"faema:DS3231\")\n"
        f"\t(at {rx} {ry} 0)\n"
        f"\t(unit 1)\n"
        f"\t(body_style 1)\n"
        f"\t(exclude_from_sim no)\n"
        f"\t(in_bom yes)\n"
        f"\t(on_board yes)\n"
        f"\t(in_pos_files yes)\n"
        f"\t(dnp no)\n"
        f"\t(uuid \"b0000012-0001-4000-8000-000000000001\")\n"
        f"\t(property \"Reference\" \"U5\"\n"
        f"\t\t(at {rx} {r(ry-16.5)} 0)\n"
        f"\t\t(show_name no)\n"
        f"\t\t(do_not_autoplace no)\n"
        f"\t\t(effects (font (size 1.27 1.27)))\n"
        f"\t)\n"
        f"\t(property \"Value\" \"DS3231\"\n"
        f"\t\t(at {rx} {r(ry+16.5)} 0)\n"
        f"\t\t(show_name no)\n"
        f"\t\t(do_not_autoplace no)\n"
        f"\t\t(effects (font (size 1.27 1.27)))\n"
        f"\t)\n"
        f"\t(property \"Footprint\" \"\"\n"
        f"\t\t(at {rx} {ry} 0)\n"
        f"\t\t(hide yes)\n"
        f"\t\t(show_name no)\n"
        f"\t\t(do_not_autoplace no)\n"
        f"\t\t(effects (font (size 1.27 1.27)))\n"
        f"\t)\n"
        f"\t(property \"Datasheet\" \"\"\n"
        f"\t\t(at {rx} {ry} 0)\n"
        f"\t\t(hide yes)\n"
        f"\t\t(show_name no)\n"
        f"\t\t(do_not_autoplace no)\n"
        f"\t\t(effects (font (size 1.27 1.27)))\n"
        f"\t)\n"
        f"\t(property \"Description\" \"\"\n"
        f"\t\t(at {rx} {ry} 0)\n"
        f"\t\t(show_name no)\n"
        f"\t\t(do_not_autoplace no)\n"
        f"\t\t(effects (font (size 1.27 1.27)))\n"
        f"\t)\n"
        + ds_pins_str("0000012", ds_pins) +
        f"\t(instances\n"
        f"\t\t(project \"faema-president\"\n"
        f"\t\t\t(path \"/a0000000-0000-4000-8000-000000000001\"\n"
        f"\t\t\t\t(reference \"U5\")\n"
        f"\t\t\t\t(unit 1)\n"
        f"\t\t\t)\n"
        f"\t\t)\n"
        f"\t)\n"
        f")\n"
    )

    # BT1 Conn_2pin (CR2032)
    out.append(comp("faema:Conn_2pin", 325, 155, 0, "BT1", "CR2032",
                    "0000013", [1,2],
                    ref_dy=-6.4, val_dy=6.3))

    # R7 — UPDATED value 220R
    out.append(
        "(symbol\n"
        "\t(lib_id \"faema:R\")\n"
        "\t(at 190 72 0)\n"
        "\t(unit 1)\n"
        "\t(body_style 1)\n"
        "\t(exclude_from_sim no)\n"
        "\t(in_bom yes)\n"
        "\t(on_board yes)\n"
        "\t(in_pos_files yes)\n"
        "\t(dnp no)\n"
        "\t(uuid \"b0000020-0001-4000-8000-000000000001\")\n"
        "\t(property \"Reference\" \"R7\"\n"
        "\t\t(at 192.8 72 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Value\" \"220R\"\n"
        "\t\t(at 187 72 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Footprint\" \"\"\n"
        "\t\t(at 190 72 0)\n"
        "\t\t(hide yes)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Datasheet\" \"\"\n"
        "\t\t(at 190 72 0)\n"
        "\t\t(hide yes)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Description\" \"\"\n"
        "\t\t(at 190 72 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(pin \"1\" (uuid \"c0000020-0001-4000-8000-000000000001\"))\n"
        "\t(pin \"2\" (uuid \"c0000020-0001-4000-8000-000000000002\"))\n"
        "\t(instances\n"
        "\t\t(project \"faema-president\"\n"
        "\t\t\t(path \"/a0000000-0000-4000-8000-000000000001\"\n"
        "\t\t\t\t(reference \"R7\")\n"
        "\t\t\t\t(unit 1)\n"
        "\t\t\t)\n"
        "\t\t)\n"
        "\t)\n"
        ")\n"
    )

    # R9 10k PD
    out.append(comp("faema:R", 200, 104, 0, "R9", "10k PD",
                    "0000021", [1,2],
                    ref_dx=2.8, ref_dy=0, val_dx=-3, val_dy=0))

    # R10 470R
    out.append(comp("faema:R", 250, 250, 0, "R10", "470R",
                    "0000022", [1,2],
                    ref_dx=2.8, ref_dy=0, val_dx=-3, val_dy=0))

    # D1 LED
    out.append(comp("faema:LED", 235, 250, 0, "D1", "LED_GREEN",
                    "0000023", [1,2],
                    ref_dy=-3.54, val_dy=3.51))

    # R11 100k (horizontal, rot=90)
    out.append(
        "(symbol\n"
        "\t(lib_id \"faema:R\")\n"
        "\t(at 45 250 90)\n"
        "\t(unit 1)\n"
        "\t(body_style 1)\n"
        "\t(exclude_from_sim no)\n"
        "\t(in_bom yes)\n"
        "\t(on_board yes)\n"
        "\t(in_pos_files yes)\n"
        "\t(dnp no)\n"
        "\t(uuid \"b0000024-0001-4000-8000-000000000001\")\n"
        "\t(property \"Reference\" \"R11\"\n"
        "\t\t(at 45 255 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Value\" \"100k\"\n"
        "\t\t(at 45 257 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Footprint\" \"\"\n"
        "\t\t(at 45 250 0)\n"
        "\t\t(hide yes)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Datasheet\" \"\"\n"
        "\t\t(at 45 250 0)\n"
        "\t\t(hide yes)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(property \"Description\" \"\"\n"
        "\t\t(at 45 250 0)\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size 1.27 1.27)))\n"
        "\t)\n"
        "\t(pin \"1\" (uuid \"c0000024-0001-4000-8000-000000000001\"))\n"
        "\t(pin \"2\" (uuid \"c0000024-0001-4000-8000-000000000002\"))\n"
        "\t(instances\n"
        "\t\t(project \"faema-president\"\n"
        "\t\t\t(path \"/a0000000-0000-4000-8000-000000000001\"\n"
        "\t\t\t\t(reference \"R11\")\n"
        "\t\t\t\t(unit 1)\n"
        "\t\t\t)\n"
        "\t\t)\n"
        "\t)\n"
        ")\n"
    )

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Build new component instances
# ---------------------------------------------------------------------------
def make_new_components():
    parts = []
    counters = {"sym": _sym_n}  # will be used via next_sym()

    # ----- Q1 NMOS_GSD -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:NMOS_GSD", 190, 97, 0, "Q1", "2N7002", n,
        ["1","2","3"],
        ref_off_x=192.5, ref_off_y=93.5,
        val_off_x=192.5, val_off_y=95.0
    ))

    # ----- R_gate -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 174, 97, 90, "R_gate", "100R", n,
        ["1","2"],
        ref_off_x=174, ref_off_y=99.5,
        val_off_x=174, val_off_y=101.5
    ))

    # ----- F1 Fuse at (47, 28) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:Fuse", 47, 28, 0, "F1", "T16A", n,
        ["1","2"],
        ref_off_x=49.5, ref_off_y=28,
        val_off_x=44.5, val_off_y=28
    ))

    # ----- RV1 MOV at (65, 28) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:MOV", 65, 28, 0, "RV1", "S14K275", n,
        ["1","2"],
        ref_off_x=67.5, ref_off_y=28,
        val_off_x=62.5, val_off_y=28
    ))

    # ----- Input/output decoupling -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 182, 28, 0, "C1", "10u/16V", n,
        ["1","2"],
        ref_off_x=184.5, ref_off_y=28,
        val_off_x=179.5, val_off_y=28
    ))

    # ----- C2 C at (190, 28) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 197, 28, 0, "C2", "10u/16V", n,
        ["1","2"],
        ref_off_x=199.5, ref_off_y=28,
        val_off_x=194.5, val_off_y=28
    ))

    # ----- C3 C at (205, 28) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 212, 28, 0, "C3", "100n", n,
        ["1","2"],
        ref_off_x=214.5, ref_off_y=28,
        val_off_x=209.5, val_off_y=28
    ))

    # ----- C4 C at (220, 28) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 227, 28, 0, "C4", "100n", n,
        ["1","2"],
        ref_off_x=229.5, ref_off_y=28,
        val_off_x=224.5, val_off_y=28
    ))

    # ----- Rref R horizontal at (92, 155) rot=90 -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 92, 160, 90, "Rref", "430R 0.1%", n,
        ["1","2"],
        ref_off_x=92, ref_off_y=162.5,
        val_off_x=92, val_off_y=164.5
    ))

    # ----- C7 C at (100, 155) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 100, 160, 0, "C7", "100n", n,
        ["1","2"],
        ref_off_x=102.5, ref_off_y=160,
        val_off_x=97.5, val_off_y=160
    ))

    # ----- C10 C at (110, 155) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 110, 160, 0, "C10", "100n", n,
        ["1","2"],
        ref_off_x=112.5, ref_off_y=160,
        val_off_x=107.5, val_off_y=160
    ))

    # ----- Rref2 R horizontal at (92, 215) rot=90 -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 92, 235, 90, "Rref2", "430R 0.1%", n,
        ["1","2"],
        ref_off_x=92, ref_off_y=237.5,
        val_off_x=92, val_off_y=239.5
    ))

    # ----- C11 C at (100, 215) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 100, 235, 0, "C11", "100n", n,
        ["1","2"],
        ref_off_x=102.5, ref_off_y=235,
        val_off_x=97.5, val_off_y=235
    ))

    # ----- C12 C at (110, 215) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 110, 235, 0, "C12", "100n", n,
        ["1","2"],
        ref_off_x=112.5, ref_off_y=235,
        val_off_x=107.5, val_off_y=235
    ))

    # ----- R2 R horizontal at (340, 100) rot=90 -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 350, 125, 90, "R2", "4k7", n,
        ["1","2"],
        ref_off_x=350, ref_off_y=127.5,
        val_off_x=350, val_off_y=129.5
    ))

    # ----- R3 R horizontal at (350, 100) rot=90 -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 360, 125, 90, "R3", "4k7", n,
        ["1","2"],
        ref_off_x=360, ref_off_y=127.5,
        val_off_x=360, val_off_y=129.5
    ))

    # ----- C8 C at (360, 100) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 370, 125, 0, "C8", "100n", n,
        ["1","2"],
        ref_off_x=372.5, ref_off_y=125,
        val_off_x=367.5, val_off_y=125
    ))

    # ----- C9 C at (295, 110) -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:C", 255, 205, 0, "C9", "100n", n,
        ["1","2"],
        ref_off_x=257.5, ref_off_y=205,
        val_off_x=252.5, val_off_y=205
    ))

    # ----- J5 Conn_8pin at (55, 268) — ILI9341 display -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:Conn_8pin", 55, 282, 0, "J5", "ILI9341_DISP", n,
        ["1","2","3","4","5","6","7","8"],
        ref_off_x=55, ref_off_y=269.5,
        val_off_x=55, val_off_y=293
    ))

    # ----- J8 Conn_6pin at (110, 268) — preset buttons -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:Conn_6pin", 120, 282, 0, "J8", "PRESET_BTNS", n,
        ["1","2","3","4","5","6"],
        ref_off_x=120, ref_off_y=271,
        val_off_x=120, val_off_y=292
    ))

    # ----- J9 Conn_5pin at (155, 268) — encoder -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:Conn_5pin", 185, 282, 0, "J9", "ENCODER", n,
        ["1","2","3","4","5"],
        ref_off_x=185, ref_off_y=273.5,
        val_off_x=185, val_off_y=291.5
    ))

    # ----- R12 R horizontal at (115, 255) rot=90 -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 120, 265, 90, "R12", "10k", n,
        ["1","2"],
        ref_off_x=120, ref_off_y=267.5,
        val_off_x=120, val_off_y=269.5
    ))

    # ----- R13 R horizontal at (125, 255) rot=90 -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 130, 265, 90, "R13", "10k", n,
        ["1","2"],
        ref_off_x=130, ref_off_y=267.5,
        val_off_x=130, val_off_y=269.5
    ))

    # ----- R14 R horizontal at (135, 255) rot=90 -----
    n = next_sym()
    parts.append(sym_instance(
        "faema:R", 140, 265, 90, "R14", "10k", n,
        ["1","2"],
        ref_off_x=140, ref_off_y=267.5,
        val_off_x=140, val_off_y=269.5
    ))

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Build connections: power symbols + global labels + wires
# ---------------------------------------------------------------------------
def make_connections():
    items = []

    # AC input and primary protection.
    items.extend(fanout("L_IN", 19.92, 47.54, "left", "input"))
    items.extend(fanout("N_IN", 19.92, 45.00, "left", "input"))
    items.extend(fanout("PE",   19.92, 42.46, "left", "input"))
    items.extend(vertical_tap("L_IN", 45, 24.19, "up", "input"))
    items.extend(vertical_tap("L_FUSED", 45, 31.81, "down", "output"))
    items.extend(vertical_tap("N_IN", 62, 24.19, "up", "input"))
    items.extend(vertical_tap("L_FUSED", 62, 31.81, "down", "input"))

    # Mains converter and low-voltage regulation.
    items.extend(fanout("L_FUSED", 61.84, 50.08, "left", "input"))
    items.extend(fanout("N_IN", 61.84, 39.92, "left", "input"))
    items.append(power_sym("+5V", 82.16, 50.08))
    items.append(power_sym("GND", 82.16, 39.92))
    items.append(power_sym("+5V", 141.11, 47.54))
    items.append(power_sym("+3V3", 158.89, 47.54))
    items.append(power_sym("GND", 150, 36.11))

    # Bulk and ceramic decoupling around the regulator.
    items.append(power_sym("+5V", 182, 25.46))
    items.append(power_sym("GND", 182, 30.54))
    items.append(power_sym("+3V3", 197, 25.46))
    items.append(power_sym("GND", 197, 30.54))
    items.append(power_sym("+5V", 212, 25.46))
    items.append(power_sym("GND", 212, 30.54))
    items.append(power_sym("+3V3", 227, 25.46))
    items.append(power_sym("GND", 227, 30.54))

    # SSR power stage and low-side drive.
    items.append(power_sym("+5V", 190, 75.81))
    items.extend(vertical_tap("SSR_PLUS", 190, 68.19, "down", "output"))
    items.extend(vertical_tap("Q1_GATE", 200, 107.81, "up", "input"))
    items.append(power_sym("GND", 200, 100.19))
    items.extend(fanout("SSR_CTRL", 170.19, 97, "left", "input"))
    items.extend(fanout("Q1_GATE", 177.81, 97, "right", "input"))
    items.extend(vertical_tap("SSR_MINUS", 190, 93.19, "up", "input"))
    items.append(power_sym("GND", 190, 100.81))
    items.extend(fanout("AC_SSR_L_IN", 69.84, 91.08, "left", "input"))
    items.extend(fanout("AC_SSR_L_OUT", 69.84, 80.92, "left", "output"))
    items.extend(fanout("SSR_PLUS", 90.16, 91.08, "right", "input"))
    items.extend(fanout("SSR_MINUS", 90.16, 80.92, "right", "input"))
    items.extend(fanout("AC_SSR_L_OUT", 119.92, 87.27, "left", "input"))
    items.extend(fanout("N_IN", 119.92, 84.73, "left", "input"))

    # Boiler RTD front-end.
    items.append(power_sym("+3V3", 120, 166.59))
    items.append(power_sym("GND", 120, 123.41))
    items.extend(fanout("CS_MAX_CALD", 132.70, 160.24, "right", "input"))
    items.extend(fanout("SPI_MOSI", 132.70, 157.70, "right", "bidirectional"))
    items.extend(fanout("SPI_MISO", 132.70, 155.16, "right", "bidirectional"))
    items.extend(fanout("SPI_SCK", 132.70, 152.62, "right", "bidirectional"))
    items.extend(fanout("MAX_DRDY", 132.70, 147.54, "right", "input"))
    items.extend(fanout("FORCE_PLUS_U4", 107.30, 160.24, "left", "output"))
    items.extend(fanout("RTDIN_PLUS_U4", 107.30, 157.70, "left", "input"))
    items.extend(fanout("RTDIN_MINUS_U4", 107.30, 155.16, "left", "output"))
    items.extend(fanout("FORCE_MINUS_U4", 107.30, 152.62, "left", "output"))
    items.extend(fanout("REFIN_PLUS_U4", 107.30, 147.54, "left", "input"))
    items.extend(fanout("REFIN_MINUS_U4", 107.30, 145.00, "left", "input"))
    items.extend(fanout("FORCE_PLUS_U4", 54.92, 148.81, "left", "input"))
    items.extend(fanout("RTDIN_PLUS_U4", 54.92, 146.27, "left", "input"))
    items.extend(fanout("RTDIN_MINUS_U4", 54.92, 143.73, "left", "input"))
    items.extend(fanout("FORCE_MINUS_U4", 54.92, 141.19, "left", "input"))
    items.extend(fanout("REFIN_PLUS_U4", 88.19, 160.00, "left", "input"))
    items.extend(fanout("FORCE_PLUS_U4", 95.81, 160.00, "right", "output"))
    items.extend(vertical_tap("RTDIN_PLUS_U4", 100.00, 157.46, "up", "input"))
    items.extend(vertical_tap("RTDIN_MINUS_U4", 100.00, 162.54, "down", "output"))
    items.append(power_sym("+3V3", 110.00, 157.46))
    items.append(power_sym("GND", 110.00, 162.54))

    # Group RTD front-end.
    items.append(power_sym("+3V3", 120, 241.59))
    items.append(power_sym("GND", 120, 198.41))
    items.extend(fanout("CS_MAX_GRUPO", 132.70, 235.24, "right", "input"))
    items.extend(fanout("SPI_MOSI", 132.70, 232.70, "right", "bidirectional"))
    items.extend(fanout("SPI_MISO", 132.70, 230.16, "right", "bidirectional"))
    items.extend(fanout("SPI_SCK", 132.70, 227.62, "right", "bidirectional"))
    items.extend(fanout("FORCE_PLUS_U6", 107.30, 235.24, "left", "output"))
    items.extend(fanout("RTDIN_PLUS_U6", 107.30, 232.70, "left", "input"))
    items.extend(fanout("RTDIN_MINUS_U6", 107.30, 230.16, "left", "output"))
    items.extend(fanout("FORCE_MINUS_U6", 107.30, 227.62, "left", "output"))
    items.extend(fanout("REFIN_PLUS_U6", 107.30, 222.54, "left", "input"))
    items.extend(fanout("REFIN_MINUS_U6", 107.30, 220.00, "left", "input"))
    items.extend(fanout("FORCE_PLUS_U6", 54.92, 223.81, "left", "input"))
    items.extend(fanout("RTDIN_PLUS_U6", 54.92, 221.27, "left", "input"))
    items.extend(fanout("RTDIN_MINUS_U6", 54.92, 218.73, "left", "input"))
    items.extend(fanout("FORCE_MINUS_U6", 54.92, 216.19, "left", "input"))
    items.extend(fanout("REFIN_PLUS_U6", 88.19, 235.00, "left", "input"))
    items.extend(fanout("FORCE_PLUS_U6", 95.81, 235.00, "right", "output"))
    items.extend(vertical_tap("RTDIN_PLUS_U6", 100.00, 232.46, "up", "input"))
    items.extend(vertical_tap("RTDIN_MINUS_U6", 100.00, 237.54, "down", "output"))
    items.append(power_sym("+3V3", 110.00, 232.46))
    items.append(power_sym("GND", 110.00, 237.54))

    # RTC and backup battery.
    items.append(power_sym("+3V3", 360, 170.24))
    items.append(power_sym("GND", 360, 139.76))
    items.extend(fanout("VBAT_RTC", 349.84, 160.08, "left", "input"))
    items.extend(fanout("I2C_SDA", 370.16, 162.62, "right", "bidirectional"))
    items.extend(fanout("I2C_SCL", 370.16, 160.08, "right", "bidirectional"))
    items.extend(fanout("VBAT_RTC", 319.92, 156.27, "left", "input"))
    items.append(power_sym("GND", 319.92, 153.73))
    items.append(power_sym("+3V3", 346.19, 125.00))
    items.extend(fanout("I2C_SDA", 353.81, 125.00, "right", "bidirectional"))
    items.append(power_sym("+3V3", 356.19, 125.00))
    items.extend(fanout("I2C_SCL", 363.81, 125.00, "right", "bidirectional"))
    items.append(power_sym("+3V3", 370.00, 122.46))
    items.append(power_sym("GND", 370.00, 127.54))

    # MCU fanout.
    items.append(power_sym("+3V3", 258.49, 203.02))
    items.append(power_sym("GND", 258.49, 200.48))
    items.extend(fanout("SPI_SCK", 258.49, 195.40, "left", "bidirectional"))
    items.extend(fanout("SPI_MOSI", 258.49, 192.86, "left", "bidirectional"))
    items.extend(fanout("SPI_MISO", 258.49, 190.32, "left", "bidirectional"))
    items.extend(fanout("CS_MAX_CALD", 258.49, 187.78, "left", "output"))
    items.extend(fanout("MAX_DRDY", 258.49, 182.70, "left", "input"))
    items.extend(fanout("SSR_CTRL", 258.49, 180.16, "left", "output"))
    items.extend(fanout("LED_STATUS", 258.49, 177.62, "left", "output"))
    items.extend(fanout("LEVEL_SENSE", 258.49, 172.54, "left", "input"))
    items.extend(fanout("CS_MAX_GRUPO", 258.49, 170.00, "left", "output"))
    items.extend(fanout("CS_DISP", 291.51, 203.02, "right", "output"))
    items.extend(fanout("DC_DISP", 291.51, 200.48, "right", "output"))
    items.extend(fanout("RST_DISP", 291.51, 197.94, "right", "output"))
    items.extend(fanout("I2C_SCL", 291.51, 192.86, "right", "bidirectional"))
    items.extend(fanout("I2C_SDA", 291.51, 190.32, "right", "bidirectional"))
    items.extend(fanout("ENC_CLK", 291.51, 185.24, "right", "input"))
    items.extend(fanout("ENC_DT", 291.51, 182.70, "right", "input"))
    items.extend(fanout("ENC_SW", 291.51, 180.16, "right", "input"))
    items.extend(fanout("BTN1", 291.51, 175.08, "right", "input"))
    items.extend(fanout("BTN2", 291.51, 172.54, "right", "input"))
    items.extend(fanout("BTN3", 291.51, 170.00, "right", "input"))
    items.append(power_sym("+3V3", 255.00, 202.46))
    items.append(power_sym("GND", 255.00, 207.54))

    # Display and UI headers.
    items.append(power_sym("+3V3", 49.92, 290.89))
    items.append(power_sym("GND", 49.92, 288.35))
    items.extend(fanout("CS_DISP", 49.92, 285.81, "left", "input"))
    items.extend(fanout("RST_DISP", 49.92, 283.27, "left", "input"))
    items.extend(fanout("DC_DISP", 49.92, 280.73, "left", "input"))
    items.extend(fanout("SPI_MOSI", 49.92, 278.19, "left", "bidirectional"))
    items.extend(fanout("SPI_SCK", 49.92, 275.65, "left", "bidirectional"))
    items.append(power_sym("+3V3", 49.92, 273.11))

    items.extend(fanout("BTN1", 114.92, 288.35, "left", "input"))
    items.extend(fanout("BTN2", 114.92, 285.81, "left", "input"))
    items.extend(fanout("BTN3", 114.92, 283.27, "left", "input"))
    items.append(power_sym("+3V3", 114.92, 280.73))
    items.append(power_sym("GND", 114.92, 278.19))
    items.append(power_sym("GND", 114.92, 275.65))

    items.extend(fanout("ENC_CLK", 179.92, 287.08, "left", "input"))
    items.extend(fanout("ENC_DT", 179.92, 284.54, "left", "input"))
    items.extend(fanout("ENC_SW", 179.92, 282.00, "left", "input"))
    items.append(power_sym("+3V3", 179.92, 279.46))
    items.append(power_sym("GND", 179.92, 276.92))

    items.append(power_sym("+3V3", 116.19, 265.00))
    items.extend(fanout("BTN1", 123.81, 265.00, "right", "output"))
    items.append(power_sym("+3V3", 126.19, 265.00))
    items.extend(fanout("BTN2", 133.81, 265.00, "right", "output"))
    items.append(power_sym("+3V3", 136.19, 265.00))
    items.extend(fanout("BTN3", 143.81, 265.00, "right", "output"))

    items.append(power_sym("+3V3", 41.19, 250.00))
    items.extend(fanout("LEVEL_SENSE", 48.81, 250.00, "right", "output"))
    items.extend(fanout("LEVEL_SENSE", 54.92, 251.27, "left", "input"))
    items.append(power_sym("GND", 54.92, 248.73))

    items.extend(fanout("LED_STATUS", 231.19, 250.00, "left", "input"))
    items.append(wire(238.81, 250.00, 250.00, 250.00))
    items.append(power_sym("GND", 250.00, 246.19))

    return "\n".join(items)


# ---------------------------------------------------------------------------
# Preserve existing text annotations and global labels from Rev.4
# ---------------------------------------------------------------------------
EXISTING_TEXTS_AND_LABELS = r"""(text "FAEMA PRESIDENT - Rev.5\nEsquemático reorganizado por blocos funcionais."
	(exclude_from_sim no)
	(at 20 294 0)
	(effects
		(font
			(size 2.2 2.2)
		)
	)
	(uuid "e0000001-0001-4000-8000-000000000001")
)
(text "ENTRADA AC / PROTEÇÕES"
	(exclude_from_sim no)
	(at 18 14 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000002-0001-4000-8000-000000000001")
)
(text "FONTE 5V / 3V3"
	(exclude_from_sim no)
	(at 145 14 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000003-0001-4000-8000-000000000001")
)
(text "MCU / CONTROLE"
	(exclude_from_sim no)
	(at 245 118 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000004-0001-4000-8000-000000000001")
)
(text "SENSOR PT100 CALDEIRA"
	(exclude_from_sim no)
	(at 42 118 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000005-0001-4000-8000-000000000001")
)
(text "SENSOR PT100 GRUPO"
	(exclude_from_sim no)
	(at 42 206 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000006-0001-4000-8000-000000000001")
)
(text "DRIVE SSR / SEGURANÇA"
	(exclude_from_sim no)
	(at 165 82 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000007-0001-4000-8000-000000000001")
)
(text "RTC"
	(exclude_from_sim no)
	(at 330 118 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000008-0001-4000-8000-000000000001")
)
(text "DISPLAY / UI"
	(exclude_from_sim no)
	(at 42 258 0)
	(effects
		(font
			(size 2 2)
			(bold yes)
		)
	)
	(uuid "e0000009-0001-4000-8000-000000000001")
)
(text "R9: pull-down de segurança\nQ1 desliga o SSR por low-side."
	(exclude_from_sim no)
	(at 210 108 0)
	(effects
		(font
			(size 1.27 1.27)
		)
		(justify left)
	)
	(uuid "e0000010-0001-4000-8000-000000000001")
)
"""

TITLE_BLOCK = """\t(title_block
\t\t(title "Faema President - Controle de Temperatura")
\t\t(rev "5.0")
\t\t(comment 1 "ESP32-S3 Mini + MicroPython")
\t\t(comment 2 "PID caldeira + feedforward grupo + agendamento")
\t)"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Reading existing schematic: {INPUT_SCH}")
    existing_lib_content = extract_lib_symbols(INPUT_SCH)
    print("  lib_symbols extracted OK")

    # Build lib_symbols block: existing + new symbols
    lib_symbols_block = (
        "(lib_symbols\n"
        + existing_lib_content
        + NEW_LIB_SYMBOLS
        + "\n)"
    )

    # Build component instances
    existing_comps = make_existing_components()
    new_comps = make_new_components()
    connections = make_connections()

    # Assemble full schematic
    sch = (
        "(kicad_sch\n"
        "\t(version 20260306)\n"
        "\t(generator \"eeschema\")\n"
        "\t(generator_version \"10.0\")\n"
        "\t(uuid \"a0000000-0000-4000-8000-000000000001\")\n"
        "\t(paper \"A3\")\n"
        + TITLE_BLOCK + "\n"
        + lib_symbols_block + "\n"
        + EXISTING_TEXTS_AND_LABELS + "\n"
        + existing_comps + "\n"
        + new_comps + "\n"
        + connections + "\n"
        "\t(sheet_instances\n"
        "\t\t(path \"/\"\n"
        "\t\t\t(page \"1\")\n"
        "\t\t)\n"
        "\t)\n"
        "\t(embedded_fonts no)\n"
        ")\n"
    )

    print(f"Writing output: {OUTPUT_SCH}")
    with open(OUTPUT_SCH, "w", encoding="utf-8") as f:
        f.write(sch)

    # Summary
    sym_count_existing = 19    # J1..BT1, R7, R9, R10, D1, R11 = 19 instances
    sym_count_new = _sym_n - 0x100
    lbl_count = _lbl_n - 0x200
    pwr_count = _pwr_n - 0x100
    wire_count = _wire_n - 0x100

    print("\n=== Generation Summary ===")
    print(f"  Existing components preserved: {sym_count_existing}")
    print(f"  New component instances added: {sym_count_new}")
    print(f"  New global labels added:       {lbl_count}")
    print(f"  New power symbols added:       {pwr_count}")
    print(f"  Wires added:                   {wire_count}")
    print(f"  New lib symbols:               6 (NMOS_GSD, Fuse, MOV, Conn_5pin, Conn_6pin, Conn_8pin)")
    print(f"  Rev updated:                   4.0 → 5.0")
    print(f"  R7 value updated:              100R → 220R")
    print(f"\nOutput written to: {OUTPUT_SCH}")
    print("Done.")


if __name__ == "__main__":
    main()
