function css(name) {
  return "rgb(" + getComputedStyle(document.documentElement).getPropertyValue(name) + ")";
}

Chart.defaults.font.size = 14;

// blowfish の元実装では backgroundColor が --color-primary-300 に固定されるため、
// Colors プラグインの自動配色が無効になり、データセットごとの色分けが効かなくなる。
// この override では backgroundColor の固定を外し、他のテーマ連動スタイルは維持する。
Chart.defaults.elements.point.borderColor = css("--color-primary-400");
Chart.defaults.elements.bar.borderColor = css("--color-primary-500");
Chart.defaults.elements.bar.borderWidth = 1;
Chart.defaults.elements.line.borderColor = css("--color-primary-400");
Chart.defaults.elements.arc.backgroundColor = css("--color-primary-200");
Chart.defaults.elements.arc.borderColor = css("--color-primary-500");
Chart.defaults.elements.arc.borderWidth = 1;
