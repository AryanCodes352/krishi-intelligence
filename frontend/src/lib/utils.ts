import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatINR(value: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);
}

export function getRiskColor(level: string) {
  switch (level?.toUpperCase()) {
    case 'LOW':
      return 'text-risk-low bg-green-50 border-green-200';
    case 'MEDIUM':
      return 'text-risk-medium bg-amber-50 border-amber-200';
    case 'HIGH':
    case 'CRITICAL':
      return 'text-risk-high bg-red-50 border-red-200';
    default:
      return 'text-gray-700 bg-gray-50 border-gray-200';
  }
}
