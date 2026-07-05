interface CardProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export function Card({ title, description, children, className = "", onClick }: CardProps) {
  return (
    <div
      className={`border rounded-xl p-5 bg-white hover:shadow-md transition ${className}`}
      onClick={onClick}
      role={onClick ? "button" : undefined}
    >
      <h3 className="text-lg font-semibold mb-1">{title}</h3>
      {description && <p className="text-gray-600 text-sm mb-3">{description}</p>}
      {children}
    </div>
  );
}