'use client';
import React from 'react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="font-sans min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-red-100 max-w-md w-full text-center">
          <h2 className="text-2xl font-bold text-red-700 mb-2">Application Error</h2>
          <p className="text-gray-600 mb-6 text-sm">
            A critical error occurred while initializing the application.
          </p>
          <button
            onClick={() => reset()}
            className="px-5 py-2.5 bg-green-700 hover:bg-green-800 text-white rounded-lg font-medium text-sm transition-colors"
          >
            Refresh Application
          </button>
        </div>
      </body>
    </html>
  );
}
