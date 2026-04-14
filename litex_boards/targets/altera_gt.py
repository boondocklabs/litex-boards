#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *

from litex.gen import *

from litex.build.io import DDROutput

from litex_boards.platforms import altera_gt

from litex.soc.cores.clock import CycloneVPLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.video import VideoVGAPHY
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster

from litedram.phy.c5ddrphy import CycloneVDDRPHY
from litedram.modules import MT41K128M16


class CycloneVDDIOOut(Module):
    def __init__(self,
        datainhi,
        datainlo,
        dataout,
        clkhi=None,
        clklo=None,
        muxsel=None,
        ena=None,
        areset=None,
        sreset=None,
        hrbypass=None,
        power_up="low",
        async_mode="none",
        sync_mode="none",
        half_rate_mode="false",
        use_new_clocking_model="false"):

        dfflo = Signal()
        dffhi = Signal()

        if clkhi is None:
            clkhi = Signal()
        if clklo is None:
            clklo = Signal()
        if muxsel is None:
            muxsel = Signal()
        if ena is None:
            ena = 1
        if areset is None:
            areset = 0
        if sreset is None:
            sreset = 0
        if hrbypass is None:
            hrbypass = 0

        self.specials += Instance("cyclonev_ddio_out",
            p_power_up               = power_up,
            p_async_mode             = async_mode,
            p_sync_mode              = sync_mode,
            p_half_rate_mode         = half_rate_mode,
            p_use_new_clocking_model = use_new_clocking_model,

            i_datainhi = datainhi,
            i_datainlo = datainlo,
            i_clkhi    = clkhi,
            i_clklo    = clklo,
            i_muxsel   = muxsel,
            i_ena      = ena,
            i_areset   = areset,
            i_sreset   = sreset,
            i_hrbypass = hrbypass,

            o_dataout  = dataout,
            o_dfflo    = dfflo,
            o_dffhi    = dffhi,
        )

class CycloneVIOIBuf(Module):
    def __init__(self, i, o, ibar=None, differential_mode="false", bus_hold="false"):
        kwargs = dict(
            p_bus_hold = bus_hold,
            i_i        = i,
            o_o        = o,
            i_dynamicterminationcontrol = 0,
        )
        if differential_mode == "true":
            kwargs["p_differential_mode"] = "true"
            kwargs["i_ibar"] = ibar
        self.specials += Instance("cyclonev_io_ibuf", **kwargs)

class CycloneVDelayChain(Module):
    def __init__(self, datain, delayctrlin, dataout):
        self.specials += Instance("cyclonev_delay_chain",
            i_datain      = datain,
            i_delayctrlin = delayctrlin,
            o_dataout     = dataout,
        )


# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_sys2x  = ClockDomain()
        self.cd_sys_ps = ClockDomain()

        # # #

        # Clk / Rst
        clk50 = platform.request("clk50")

        # PLL
        self.pll = pll = CycloneVPLL(speedgrade="-I7")
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk50, 50e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq)

        # 2x clock for 1:2 DDR PHY operation.
        pll.create_clkout(self.cd_sys2x, 2*sys_clk_freq)

        # phase-shifted system clock.
        pll.create_clkout(self.cd_sys_ps, sys_clk_freq, phase=90)



# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=50e6,
        with_led_chaser     = True,
        **kwargs):
        platform = altera_gt.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on CycloneV-GT", **kwargs)

        ddram_pads = platform.request("ddram")
        sw = platform.request_all("sw")

        self.q0 = Signal();
        self.q1 = Signal();

        CycloneVDDIOOut(sw[0], sw[1], ddram_pads.dqs_p[0])
        CycloneVDelayChain(0, 1, ddram_pads.dqs_p[0])


        """
        self.ddrphy = CycloneVDDRPHY(
            pads         = ddram_pads,
            sys_clk_freq = sys_clk_freq,
            # cl/cwl can be left None to auto-derive from tCK,
            # or set explicitly if needed.
            # cl=6,
            # cwl=5,
            # cmd_delay=0,
            # clk_polarity=0,
        )

        self.add_sdram(
            "sdram",
            phy                     = self.ddrphy,
            module                  = MT41K128M16(sys_clk_freq, "1:2"),
        )
        """

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        self.i2c = I2CMaster(platform.request("lcd"))

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=altera_gt.Platform, description="LiteX SoC on CycloneV-GT")
    parser.add_target_argument("--sys-clk-freq",        default=50e6, type=float, help="System clock frequency.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
