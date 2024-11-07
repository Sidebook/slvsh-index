"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

interface Props {
  className?: string;
}

const SearchBoxInner: React.FC<Props> = ({ className }) => {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [what, setWhat] = useState(searchParams.get("what") ?? "");
  const [who, setWho] = useState(searchParams.get("who") ?? "");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        router.push(`/search?what=${what}&who=${who}`);
      }}
      className={`flex flex-row gap-4 ${className}`}
    >
      <div className="flex flex-1 flex-row gap-4">
        <input
          type="text"
          placeholder="What"
          className="text-lg w-full px-4 py-2 bg-[#171717] border border-[#a0a0a0] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder:text-gray-400"
          value={what}
          onChange={(e) => setWhat(e.target.value)}
        />
        <input
          type="text"
          placeholder="Who"
          className="text-lg w-full px-4 py-2 bg-[#171717] border border-[#a0a0a0] rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder:text-gray-400"
          value={who}
          onChange={(e) => setWho(e.target.value)}
        />
      </div>
      <button
        type="submit"
        className="flex-0 bg-white text-black px-4 py-2 rounded-md"
      >
        Search
      </button>
    </form>
  );
};

const SearchBox: React.FC<Props> = ({ className }) => {
  return (
    <Suspense>
      <SearchBoxInner className={className} />
    </Suspense>
  );
};

export default SearchBox;
