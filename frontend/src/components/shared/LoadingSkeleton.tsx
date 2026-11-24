import React from 'react';
import { cn } from '@/lib/utils';

export const LoadingSkeleton = ({ className }: { className?: string }) => {
  return (
    <div className={cn("animate-pulse bg-gray-200 rounded", className)}></div>
  );
};

export const CardSkeleton = () => (
  <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm h-full flex flex-col">
    <LoadingSkeleton className="h-6 w-1/2 mb-4" />
    <LoadingSkeleton className="h-10 w-full mb-4" />
    <LoadingSkeleton className="h-4 w-3/4 mb-2" />
    <LoadingSkeleton className="h-4 w-5/6" />
  </div>
);
