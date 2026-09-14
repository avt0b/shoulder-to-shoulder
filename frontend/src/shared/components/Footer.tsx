const AUTHORS = [
  'Piminov M.A.',
  'Parshikov R.E.',
  'Ostrikov V.A.',
]

export function Footer() {
  return (
    <footer className="mt-auto border-t border-neutral-200 dark:border-neutral-800">
      <div className="container flex flex-col items-center justify-between gap-3 py-6 text-center sm:flex-row sm:text-left">
        <p className="text-xs text-neutral-500 dark:text-neutral-400">
          Shoulder&#8209;to&#8209;Shoulder CTF Platform
        </p>

        <div className="flex flex-col items-center gap-x-2 gap-y-1 text-xs text-neutral-500 dark:text-neutral-400 sm:flex-row sm:items-center">
          <span className="eyebrow">Group 333</span>
          <span className="hidden sm:inline text-neutral-300 dark:text-neutral-700">·</span>
          <ul className="flex flex-wrap items-center justify-center gap-x-2 gap-y-1">
            {AUTHORS.map((author, index) => (
              <li key={author} className="flex items-center gap-2">
                {index > 0 && (
                  <span className="text-neutral-300 dark:text-neutral-700">·</span>
                )}
                <span className="font-medium text-neutral-600 dark:text-neutral-300">
                  {author}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </footer>
  )
}
