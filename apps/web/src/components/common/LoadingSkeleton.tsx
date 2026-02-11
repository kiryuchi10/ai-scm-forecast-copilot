export default function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-7 bg-gray-800 rounded w-1/3" />
      <div className="h-4 bg-gray-800 rounded w-2/3" />
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-24 bg-gray-800 rounded-2xl" />
        ))}
      </div>
      <div className="h-48 bg-gray-800 rounded-2xl" />
    </div>
  );
}
