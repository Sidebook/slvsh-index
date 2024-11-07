const ResultSkeleton: React.FC = () => {
  return (
    <div className="space-y-4 animate-pulse">
      {[...Array(3)].map((_, index) => (
        <div key={index} className="border rounded-lg shadow">
          <div className="p-4">
            <div className="flex flex-row items-center">
              <div className="mr-4">
                <div className="w-32 h-16 bg-gray-300 rounded-md"></div>
              </div>
              <div className="flex-1">
                <div className="h-6 bg-gray-300 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-300 rounded w-1/4"></div>
              </div>
            </div>
          </div>
          <hr className="mx-4" />
          <div className="p-4">
            {[...Array(3)].map((_, trickIndex) => (
              <div key={trickIndex} className="flex mb-2">
                <div className="w-12 h-4 bg-gray-300 rounded mr-3"></div>
                <div className="flex-1 h-4 bg-gray-300 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ResultSkeleton;
