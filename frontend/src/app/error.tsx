'use client';
import React, { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('App runtime error:', error);
  }, [error]);

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4">
      <div className="bg-white p-8 rounded-2xl shadow-sm border border-red-100 max-w-md w-full">
        <h2 className="text-2xl font-serif font-bold text-red-700 mb-2">Something went wrong</h2>
        <p className="text-gray-600 mb-6 text-sm">
          An unexpected error occurred while loading this page.
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => reset()}
            className="px-5 py-2.5 bg-krishi-green hover:bg-krishi-green-light text-white rounded-lg font-medium text-sm transition-colors"
          >
            Try Again
          </button>
          <Link
            href="/"
            className="px-5 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium text-sm transition-colors"
          >
            Go to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
