interface InputProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  onKeyDown?: (e: React.KeyboardEvent) => void;
  type?: string;
  className?: string;
}

export function Input({
  label,
  placeholder,
  value,
  onChange,
  onKeyDown,
  type = "text",
  className = "",
}: InputProps) {
  return (
    <div className={className}>
      {label && (
        <label className="text-xs font-medium text-gray-500 mb-1 block">{label}</label>
      )}
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        onKeyDown={onKeyDown}
        className="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}