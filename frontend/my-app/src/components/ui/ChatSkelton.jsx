const ChatSkeleton = () => {
  return (
    <div className="max-w-[90%] mx-auto space-y-6 animate-pulse">

      {/* AI Message */}
      <div className="flex justify-start">
        <div className="bg-slate-800 rounded-2xl p-4 w-[70%]">
          <div className="h-4 bg-slate-700 rounded w-3/4 mb-3"></div>
          <div className="h-4 bg-slate-700 rounded w-full mb-3"></div>
          <div className="h-4 bg-slate-700 rounded w-2/3"></div>
        </div>
      </div>

      {/* User Message */}
      <div className="flex justify-end">
        <div className="bg-slate-700 rounded-2xl p-4 w-[45%]">
          <div className="h-4 bg-slate-600 rounded w-full"></div>
        </div>
      </div>

      {/* AI Message */}
      <div className="flex justify-start">
        <div className="bg-slate-800 rounded-2xl p-4 w-[75%]">
          <div className="h-4 bg-slate-700 rounded w-full mb-3"></div>
          <div className="h-4 bg-slate-700 rounded w-4/5 mb-3"></div>
          <div className="h-4 bg-slate-700 rounded w-1/2"></div>
        </div>
      </div>

    </div>
  );
};

export {ChatSkeleton}