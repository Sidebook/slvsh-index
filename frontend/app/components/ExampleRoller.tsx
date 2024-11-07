"use client";

import { useRouter } from "next/navigation";
import React, { useEffect, useRef, useState } from "react";

const ExampleRoller: React.FC = () => {
  const router = useRouter();
  const [currentExamples, setCurrentExamples] = useState<string[]>([]);
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/common_tricks`)
      .then((res) => res.json())
      .then((data) => {
        const tricks: { trick: string; count: number }[] = data.slice(0, 100);
        for (let i = tricks.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [tricks[i], tricks[j]] = [tricks[j], tricks[i]];
        }
        const picked = tricks
          .filter((trick) => trick.trick.length < 10)
          .slice(0, Math.min(5, tricks.length))
          .map((trick) => trick.trick);

        setTimeout(() => {
          setCurrentExamples(picked);
        }, 1000);
      });
  }, []);

  return (
    <div className="flex gap-2 flex-wrap whitespace-nowrap px-4 justify-center">
      {currentExamples.map((example, index) => (
        <button
          key={example}
          className="bg-[#333333] text-sm md:text-base text-white px-3 py-1 rounded-sm fade-in"
          style={{ animationDelay: `${index * 200}ms` }}
          onClick={() => {
            router.push(`/search?what=${example}`);
          }}
        >
          {example}
        </button>
      ))}
    </div>
  );
};

export default ExampleRoller;
