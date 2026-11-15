<?php
declare(strict_types=1);

/** Small building blocks shared by the admin screens. */

function icon(string $name): string
{
    $paths = [
        'dashboard' => '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
        'home' => '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
        'service' => '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
        'project' => '<rect x="3" y="4" width="18" height="14" rx="1"/><path d="M3 9h18M9 9v9M15 9v9"/><path d="M8 21h8"/>',
        'media' => '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M21 16l-5-5-8 9"/>',
        'enquiries' => '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
        'settings' => '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
        'help' => '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7"/><path d="M12 17h0"/>',
        'up' => '<path d="M6 15l6-6 6 6"/>', 'down' => '<path d="M6 9l6 6 6-6"/>', 'trash' => '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>',
        'plus' => '<path d="M12 5v14M5 12h14"/>', 'eye' => '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>',
        'warn' => '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h0"/>', 'out' => '<path d="M15 4h4v16h-4M10 8l-4 4 4 4M6 12h10"/>',
    ];
    return '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' . ($paths[$name] ?? '') . '</svg>';
}

function licence_badge(array $item): string
{
    $key = $item['licence'] ?? 'unknown';
    return '<span class="badge badge-' . e($key) . '">' . e(LICENCES[$key] ?? LICENCES['unknown']) . '</span>';
}

/** Image (or video) chooser: a preview, a hidden field holding the chosen id, and buttons. */
function picker_field(array $content, string $name, ?string $value, string $kind = 'image', string $dataName = ''): string
{
    $item = media_item($content, $value);
    $url = $item ? media_url($content, $value) : '';
    $html = '<div class="picker" data-picker data-kind="' . e($kind) . '">';
    $html .= '<input type="hidden" name="' . e($name) . '" value="' . e($item ? (string) $value : '') . '"' . ($dataName ? ' data-name="' . e($dataName) . '"' : '') . '>';
    $html .= '<div class="picker-preview" data-picker-preview>';
    if ($item && $kind === 'image') {
        $html .= '<img src="' . e($url) . '" alt="' . e($item['alt'] ?? '') . '">';
    } elseif ($item) {
        $html .= '<span class="picker-file">' . e($item['file']) . '</span>';
    } else {
        $html .= '<span class="picker-empty">No ' . e($kind) . ' chosen</span>';
    }
    $html .= '</div><div class="picker-actions">';
    $html .= '<span class="picker-warning" data-picker-warning' . ($item && media_needs_check($item) ? '' : ' hidden') . '>' . icon('warn') . ' No licence on record</span>';
    $html .= '<button type="button" class="btn btn-small" data-picker-open>Choose ' . e($kind) . '</button>';
    $html .= '<button type="button" class="btn btn-small btn-quiet" data-picker-clear' . ($item ? '' : ' hidden') . '>Remove</button>';
    return $html . '</div></div>';
}

/** Text box with a live character count and a recommended length. */
function counted_input(string $name, string $value, int $recommended, bool $multiline = false): string
{
    $attrs = 'name="' . e($name) . '" data-count="' . $recommended . '"';
    $field = $multiline ? '<textarea ' . $attrs . ' rows="3">' . e($value) . '</textarea>' : '<input type="text" ' . $attrs . ' value="' . e($value) . '">';
    return $field . '<small class="count" data-count-out></small>';
}
