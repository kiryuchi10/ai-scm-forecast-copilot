type Props = {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
};

export default function SectionCard({ title, subtitle, children }: Props) {
  return (
    <section className="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-sm">
      <div className="border-b border-gray-800 pb-4 mb-4">
        <h3 className="font-semibold text-white text-lg">{title}</h3>
        {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}
