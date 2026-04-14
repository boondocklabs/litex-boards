#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk
    ("clk50", 0, Pins("V28"), IOStandard("1.5-V")),
    ("clk125", 0, Pins("U31 U30"), IOStandard("LVDS")),

    # 100MHz programmable between 10-810MHz
    ("clktop", 0, Pins("H19 H18"), IOStandard("LVDS")),
    ("clkbot", 0, Pins("AF18 AG18"), IOStandard("LVDS")),
    ("clkright", 0, Pins("W26 W27"), IOStandard("LVDS")),
    ("refclk_ql1", 0, Pins("AA11 AB10"), IOStandard("LVDS")),
    ("refclk_ql3", 0, Pins("R10 P10"), IOStandard("LVDS")),

    # 148.5MHz programmable between 10-810MHz
    ("refclk_ql2", 0, Pins("U11 T10"), IOStandard("LVDS")),

    ("clkout_sma", 0, Pins("AF33"), IOStandard("2.5-V")),

    ("pcie_refclk", 0, Pins("W11 V10"), IOStandard("LVDS")),

    # Leds
    ("user_led", 0, Pins("AM23"), IOStandard("2.5-V")),
    ("user_led", 1, Pins("AE25"), IOStandard("2.5-V")),
    ("user_led", 2, Pins("AK29"), IOStandard("2.5-V")),
    ("user_led", 3, Pins("AL31"), IOStandard("2.5-V")),
    ("user_led", 4, Pins("AF25"), IOStandard("2.5-V")),
    ("user_led", 5, Pins("AJ27"), IOStandard("2.5-V")),
    ("user_led", 6, Pins("AC22"), IOStandard("2.5-V")),
    ("user_led", 7, Pins("AH27"), IOStandard("2.5-V")),

    ("hsma_led", 0, Pins("D12"), IOStandard("2.5-V")),
    ("hsma_led", 1, Pins("B3"), IOStandard("2.5-V")),
    ("hsmb_led", 0, Pins("B30"), IOStandard("2.5-V")),
    ("hsmb_led", 1, Pins("C24"), IOStandard("2.5-V")),

    # PCIe x1 LED
    ("pcie_led", 0, Pins("AK19"), IOStandard("2.5-V")),
    # PCIe x4 LED
    ("pcie_led", 1, Pins("AD22"), IOStandard("2.5-V")),

    # Buttons
    ("key", 0, Pins("AK13"), IOStandard("2.5-V")),
    ("key", 1, Pins("AA15"),  IOStandard("2.5-V")),
    ("key", 2, Pins("AN8"),  IOStandard("2.5-V")),

    # DIP Switches
    ("sw", 0, Pins("H12"),  IOStandard("2.5-V")),
    ("sw", 1, Pins("A2"),  IOStandard("2.5-V")),
    ("sw", 2, Pins("E10"),  IOStandard("2.5-V")),
    ("sw", 3, Pins("D9"),  IOStandard("2.5-V")),
    ("sw", 4, Pins("E9"),  IOStandard("2.5-V")),
    ("sw", 5, Pins("D7"),  IOStandard("2.5-V")),
    ("sw", 6, Pins("E8"),  IOStandard("2.5-V")),
    ("sw", 7, Pins("E7"),  IOStandard("2.5-V")),

    # 2x16 character LCD I2C
    ("lcd", 0,
        Subsignal("scl", Pins("AL6")),
        Subsignal("sda", Pins("AJ10")),
        IOStandard("2.5-V")
    ),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("HSMA:0"), IOStandard("2.5-V")),
        Subsignal("rx", Pins("HSMA:1"),  IOStandard("2.5-V"))
    ),

    # DDR3B - four x16 devices on a shared shared address and command bus
    ("ddram", 0,
        Subsignal("a", Pins(
            "H29 K28 K34 L32 R32 R33 N32 G33 "
            "AE34 L27 V33 U33 T31 T30"
        ), IOStandard("SSTL-15")),

        Subsignal("ba", Pins("J31 N29 P27"), IOStandard("SSTL-15")),
        Subsignal("ras_n",   Pins("Y32"),   IOStandard("SSTL-15")),
        Subsignal("cas_n",   Pins("N27"),   IOStandard("SSTL-15")),
        Subsignal("we_n",    Pins("AM34"),  IOStandard("SSTL-15")),
        Subsignal("cs_n",    Pins("V27"),   IOStandard("SSTL-15")),
        Subsignal("cke",     Pins("AF32"),  IOStandard("SSTL-15")),
        Subsignal("odt",     Pins("AA32"),  IOStandard("SSTL-15")),
        Subsignal("reset_n", Pins("AG31"),  IOStandard("1.5-V")),

        Subsignal("dm", Pins(
            "AE30 AE32 AC34 W34 M33 K32 L31 H28"
        ), IOStandard("SSTL-15")),

        Subsignal("dq", Pins(
            "AF31 AD30 AJ32 AC31 AH32 Y28 AN34 Y27 "
            "AD32 AH33 AB31 AJ34 AA31 AK34 W31 AG33 "
            "AD34 AC33 AG34 AB33 AE33 V32 AH34 W32 "
            "U29 V34 U34 AA33 R34 Y33 P34 U28 "
            "T32 N33 T33 L33 T28 J34 T27 M34 "
            "K33 N31 G34 R28 H33 P32 H34 R27 "
            "N28 L30 P30 K30 J32 H32 M31 H31 "
            "G30 K29 G31 M30 J30 M29 J29 L28"
        ), IOStandard("SSTL-15 CLASS I")),

        Subsignal("dqs_p", Pins("Y29 W29 V24 U24 U23 T25 R23 P24"),
            IOStandard("SSTL-15")),
        Subsignal("dqs_n", Pins("Y30 W30 V23 U25 T23 R25 R24 P25"),
            IOStandard("SSTL-15 CLASS I")),

        Subsignal("clk", Pins("R30"),
            IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
        #Subsignal("clk_p", Pins("R30"),
        #    IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
        #Subsignal("clk_n", Pins("R29"),
        #    IOStandard("DIFFERENTIAL 1.5-V SSTL CLASS I")),
    ),

    # enet_gtx_clk AP7
    # enet_intn AK10 (management bus interrupt)
    # enet_rx_clk AM10
    ("eth", 0,
        Subsignal("rst_n",   Pins("AN9")),
        Subsignal("mdio",    Pins("AG14")),
        Subsignal("mdc",     Pins("AM8")),
        Subsignal("rx_dv",   Pins("AH14")),
        #Subsignal("rx_er",   Pins("")),
        Subsignal("rx_data", Pins("AK14 AL10 AJ14 AK12")),
        Subsignal("tx_en",   Pins("AC14")),
        Subsignal("tx_data", Pins("AB14 AD15 AB15 AB13")),
        #Subsignal("col",     Pins("")),
        #Subsignal("crs",     Pins("")),
        IOStandard("2.5-V"),
    ),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # HSMC Debug Header on HSMA
    ("HSMA", "F10 G11 L12 F11 F12 K12")
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name   = "clk50"
    default_clk_period = 1e9/50e6

    def __init__(self, toolchain="quartus"):
        AlteraPlatform.__init__(self, "5CGTFD9E5F35C7", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return USBBlaster()

    def do_finalize(self, fragment):
        AlteraPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk50", loose=True), 1e9/50e6)
