"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Zap, LayoutDashboard, Activity, FlaskConical, FileSearch, Menu, X } from "lucide-react";

const links = [
  { href: "#overview", label: "Overview", icon: LayoutDashboard },
  { href: "#recovery", label: "Recovery", icon: Activity },
  { href: "#simulator", label: "Simulator", icon: FlaskConical },
  { href: "#audit", label: "Audit", icon: FileSearch },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <motion.nav initial={{ y: -24, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: .5 }} className="sticky top-0 z-50 border-b border-white/[.07] bg-[#07070b]/80 backdrop-blur-2xl">
      <div className="mx-auto max-w-[1440px] px-4 lg:px-7">
        <div className="flex items-center justify-between gap-4 py-3">
          <a href="#overview" onClick={() => setOpen(false)} className="group flex shrink-0 items-center gap-3">
            <motion.div whileHover={{ rotate: 8, scale: 1.06 }} whileTap={{ scale: .95 }} className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 shadow-lg shadow-indigo-500/20">
              <Zap className="h-5 w-5 text-white" fill="currentColor" />
            </motion.div>
            <div className="hidden sm:block"><h1 className="text-lg font-bold tracking-tight gradient-text">RecoverOps AI</h1><p className="text-[10px] text-zinc-500">Autonomous Revenue Recovery</p></div>
          </a>

          <div className="hidden items-center gap-1 rounded-2xl border border-white/[.06] bg-white/[.025] p-1 md:flex">
            {links.map(({ href, label, icon: Icon }) => <a key={href} href={href} className="group relative flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium text-zinc-400 transition-all hover:bg-white/[.07] hover:text-white"><Icon className="h-3.5 w-3.5 transition-transform group-hover:scale-110" />{label}<span className="absolute inset-x-3 -bottom-0.5 h-px scale-x-0 bg-gradient-to-r from-indigo-400 to-cyan-400 transition-transform group-hover:scale-x-100" /></a>)}
          </div>

          <div className="flex items-center gap-2">
            <div className="hidden items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/[.08] px-3 py-1.5 text-[11px] font-medium text-emerald-400 sm:flex"><motion.span animate={{ opacity:[1,.35,1], scale:[1,.8,1] }} transition={{ duration:2, repeat:Infinity }} className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Operational</div>
            <div className="hidden items-center gap-1.5 rounded-xl border border-white/[.07] bg-white/[.025] px-3 py-1.5 text-[11px] text-zinc-400 sm:flex"><Shield className="h-3.5 w-3.5" />Test Mode</div>
            <motion.button type="button" whileTap={{ scale: .92 }} onClick={() => setOpen(!open)} className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/[.08] bg-white/[.03] text-zinc-300 md:hidden" aria-label="Toggle navigation">{open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}</motion.button>
          </div>
        </div>

        <AnimatePresence>
          {open && <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden md:hidden">
            <div className="mb-3 grid grid-cols-2 gap-2 rounded-2xl border border-white/[.07] bg-white/[.025] p-2">
              {links.map(({ href, label, icon: Icon }) => <a key={href} href={href} onClick={() => setOpen(false)} className="flex items-center gap-2 rounded-xl px-3 py-3 text-xs font-medium text-zinc-400 transition-colors hover:bg-white/[.06] hover:text-white"><Icon className="h-4 w-4" />{label}</a>)}
            </div>
          </motion.div>}
        </AnimatePresence>
      </div>
    </motion.nav>
  );
}
