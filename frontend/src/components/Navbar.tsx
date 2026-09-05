"use client";

import { motion } from "framer-motion";
import { Shield, Zap, LayoutDashboard, Activity, FlaskConical, FileSearch } from "lucide-react";

const links = [
  { href: "#overview", label: "Overview", icon: LayoutDashboard },
  { href: "#recovery", label: "Recovery", icon: Activity },
  { href: "#simulator", label: "Simulator", icon: FlaskConical },
  { href: "#audit", label: "Audit", icon: FileSearch },
];

export default function Navbar() {
  return (
    <motion.nav initial={{ y: -24, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: .5 }} className="sticky top-0 z-50 border-b border-white/[.07] bg-[#07070b]/75 backdrop-blur-2xl">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-6 px-5 py-3 lg:px-7">
        <a href="#overview" className="flex shrink-0 items-center gap-3 group">
          <motion.div whileHover={{ rotate: 8, scale: 1.06 }} className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-400 shadow-lg shadow-indigo-500/20">
            <Zap className="h-5 w-5 text-white" fill="currentColor" />
          </motion.div>
          <div className="hidden sm:block">
            <h1 className="text-lg font-bold tracking-tight gradient-text">RecoverOps AI</h1>
            <p className="text-[10px] text-zinc-500">Autonomous Revenue Recovery</p>
          </div>
        </a>

        <div className="hidden md:flex items-center gap-1 rounded-2xl border border-white/[.06] bg-white/[.025] p-1">
          {links.map(({ href, label, icon: Icon }) => (
            <a key={href} href={href} className="flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium text-zinc-400 transition-all hover:bg-white/[.07] hover:text-white">
              <Icon className="h-3.5 w-3.5" />{label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/[.08] px-3 py-1.5 text-[11px] font-medium text-emerald-400">
            <motion.span animate={{ opacity:[1,.35,1], scale:[1,.8,1] }} transition={{ duration:2, repeat:Infinity }} className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            Operational
          </div>
          <div className="hidden sm:flex items-center gap-1.5 rounded-xl border border-white/[.07] bg-white/[.025] px-3 py-1.5 text-[11px] text-zinc-400"><Shield className="h-3.5 w-3.5" />Test Mode</div>
        </div>
      </div>
    </motion.nav>
  );
}
