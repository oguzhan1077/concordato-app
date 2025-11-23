function Logo({ className = "", size = "default", showText = true }) {
  // Size options: "sm", "default", "lg"
  const sizeClasses = {
    sm: "w-6 h-6",
    default: "w-8 h-8",
    lg: "w-12 h-12"
  };

  const textSizeClasses = {
    sm: "text-sm",
    default: "text-lg",
    lg: "text-2xl"
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Logo Icon - Belge ve Takip Teması */}
      <div className={`${sizeClasses[size]} relative flex items-center justify-center`}>
        <svg
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full"
        >
          {/* Ana Belge Şekli */}
          <rect
            x="8"
            y="6"
            width="32"
            height="40"
            rx="2"
            className="fill-blue-600 dark:fill-blue-500"
          />
          
          {/* Belge İçi Çizgiler (İlan Listesi Teması) */}
          <line
            x1="14"
            y1="16"
            x2="34"
            y2="16"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            className="opacity-90"
          />
          <line
            x1="14"
            y1="22"
            x2="30"
            y2="22"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            className="opacity-70"
          />
          <line
            x1="14"
            y1="28"
            x2="28"
            y2="28"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            className="opacity-60"
          />
          
          {/* Takip/İzleme İkonu - Göz veya Radar */}
          <circle
            cx="36"
            cy="12"
            r="6"
            className="fill-white dark:fill-gray-100"
          />
          <circle
            cx="36"
            cy="12"
            r="3"
            className="fill-blue-600 dark:fill-blue-500"
          />
          
          {/* Vurgu - Parlama Efekti */}
          <rect
            x="8"
            y="6"
            width="32"
            height="8"
            rx="2"
            className="fill-blue-400 dark:fill-blue-400 opacity-30"
          />
        </svg>
      </div>

      {/* Logo Metni */}
      {showText && (
        <span className={`font-bold text-gray-900 dark:text-white ${textSizeClasses[size]}`}>
          Konkordato Takip
        </span>
      )}
    </div>
  );
}

export default Logo;

