import SearchBox from "./components/searchBox";

export default function Home() {
  return (
    <div className="flex flex-col items-center min-w-screen min-h-screen">
      <div className="flex-1 flex flex-col justify-center">
        <div className="flex flex-col text-center">
          <h1 className="font-bold text-[2rem] md:text-[3rem]">SLVSH INDEX</h1>
          <div className="text-sm md:text-base text-gray-300">
            Find tricks from the past ALL SLVSH matches!
          </div>
        </div>
      </div>
      <main className="w-full max-w-3xl p-8">
        <SearchBox />
      </main>
      <div className="flex-1" />
      <footer className="text-sm text-gray-100 p-4">
        Made by{" "}
        <span>
          <a href="https://instagram.com/ryu_ski" target="_blank">
            @ryu_ski
          </a>
        </span>
      </footer>
    </div>
  );
}
