window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        geoStyle: function(feature, context) {
            var props = feature.properties || {};
            var style = props.style || {};
            var selectedCode = context && context.hideout && context.hideout.selected_code;
            var isSelected = (selectedCode && (props.code === selectedCode || props.ADM1_PCODE === selectedCode || props.ADM2_PCODE === selectedCode));
            
            return {
                fillColor: style.fillColor || '#2b6cb0',
                weight: isSelected ? 3.5 : (style.weight || 1.2),
                opacity: 1,
                color: isSelected ? '#ffb703' : (style.color || '#ffffff'),
                fillOpacity: isSelected ? 0.95 : (style.fillOpacity !== undefined ? style.fillOpacity : 0.75),
                dashArray: isSelected ? '4, 4' : ''
            };
        },
        onEachFeature: function(feature, layer, context) {
            if (feature.properties && feature.properties.tooltip_html) {
                layer.bindTooltip(feature.properties.tooltip_html, {
                    sticky: true,
                    className: 'custom-map-tooltip',
                    direction: 'top'
                });
            }
        }
    }
});