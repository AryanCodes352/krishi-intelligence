'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Leaf } from 'lucide-react';
import { cn } from '@/lib/utils';

export const Navbar = () => {
  const pathname = usePathname();
  const isFarmRoute = pathname?.startsWith('/farm/');
  const farmId = isFarmRoute ? pathname.split('/')[2] : null;

  return (
    <nav className="bg-krishi-green-dark text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2">
              <Leaf className="w-6 h-6 text-krishi-gold" />
              <span className="font-serif font-bold text-xl tracking-wide text-krishi-cream">
                KRISHI <span className="text-krishi-gold">INTELLIGENCE</span>
              </span>
            </Link>
          </div>
          
          {isFarmRoute && farmId && (
            <div className="hidden md:flex items-center space-x-1">
              <NavLink href={`/farm/${farmId}`} label="Dashboard" active={pathname === `/farm/${farmId}`} />
              <NavLink href={`/farm/${farmId}/digital-twin`} label="Digital Twin" active={pathname === `/farm/${farmId}/digital-twin`} />
              <NavLink href={`/farm/${farmId}/decision`} label="Decision" active={pathname === `/farm/${farmId}/decision`} />
              <NavLink href={`/farm/${farmId}/weather`} label="Weather" active={pathname === `/farm/${farmId}/weather`} />
              <NavLink href={`/farm/${farmId}/market`} label="Market" active={pathname === `/farm/${farmId}/market`} />
              <NavLink href={`/farm/${farmId}/soil`} label="Soil" active={pathname === `/farm/${farmId}/soil`} />
              <NavLink href={`/farm/${farmId}/expert`} label="Expert" active={pathname === `/farm/${farmId}/expert`} />
            </div>
          )}
        </div>
      </div>
      
      {/* Mobile nav scrollable strip */}
      {isFarmRoute && farmId && (
        <div className="md:hidden border-t border-krishi-green/30 bg-krishi-green-dark/95 overflow-x-auto">
          <div className="flex px-4 py-2 space-x-4">
            <MobileNavLink href={`/farm/${farmId}`} label="Overview" active={pathname === `/farm/${farmId}`} />
            <MobileNavLink href={`/farm/${farmId}/digital-twin`} label="Digital Twin" active={pathname === `/farm/${farmId}/digital-twin`} />
            <MobileNavLink href={`/farm/${farmId}/decision`} label="Decision" active={pathname === `/farm/${farmId}/decision`} />
            <MobileNavLink href={`/farm/${farmId}/weather`} label="Weather" active={pathname === `/farm/${farmId}/weather`} />
            <MobileNavLink href={`/farm/${farmId}/market`} label="Market" active={pathname === `/farm/${farmId}/market`} />
            <MobileNavLink href={`/farm/${farmId}/soil`} label="Soil" active={pathname === `/farm/${farmId}/soil`} />
            <MobileNavLink href={`/farm/${farmId}/expert`} label="Expert" active={pathname === `/farm/${farmId}/expert`} />
          </div>
        </div>
      )}
    </nav>
  );
};

const NavLink = ({ href, label, active }: { href: string; label: string; active: boolean }) => (
  <Link 
    href={href} 
    className={cn(
      "px-3 py-2 rounded-md text-sm font-medium transition-colors",
      active ? "bg-krishi-green text-white" : "text-gray-300 hover:bg-krishi-green/50 hover:text-white"
    )}
  >
    {label}
  </Link>
);

const MobileNavLink = ({ href, label, active }: { href: string; label: string; active: boolean }) => (
  <Link 
    href={href} 
    className={cn(
      "whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-medium transition-colors border",
      active ? "bg-krishi-green border-krishi-green text-white" : "border-gray-500 text-gray-300 hover:bg-krishi-green/50"
    )}
  >
    {label}
  </Link>
);
