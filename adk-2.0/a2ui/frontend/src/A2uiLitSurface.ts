import { LitElement, html, css } from 'lit';

export class A2uiLitSurface extends LitElement {
  static properties = {
    data: { type: Object }
  };

  data: any = {};

  static styles = css`
    .a2ui-surface {
      margin-top: 10px;
      border: 1px solid #000;
      padding: 10px;
      border-radius: 4px;
      background: #f0f0f0;
    }
    .card {
      border: 1px solid #ddd;
      padding: 10px;
      border-radius: 4px;
      margin-bottom: 10px;
      background: #fff;
    }
    .column {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }
    .error {
      color: red;
    }
  `;

  render() {
    if (!this.data) return html``;

    const components = this.data.updateComponents?.components || 
                       (Array.isArray(this.data) ? this.data : [this.data]);

    const componentMap = new Map<string, any>();
    components.forEach((item: any) => {
      if (item.id) componentMap.set(item.id, item);
    });

    const renderComponent = (id: string): any => {
      try {
        const item = componentMap.get(id);
        if (!item) return html`<div class="error">Component not found: ${id}</div>`;

        const type = item.type || item.component;
        const props = item.props || item;
        const children = item.children || (item.child ? [item.child] : []);

        switch (type) {
          case 'Card':
            return html`
              <div class="card">
                ${props.title ? html`<h4>${props.title}</h4>` : ''}
                ${props.description ? html`<p>${props.description}</p>` : ''}
                ${children.map((childId: string) => renderComponent(childId))}
              </div>
            `;
          case 'Heading':
            const level = props.level || 1;
            if (level === 1) return html`<h1>${props.text}</h1>`;
            if (level === 2) return html`<h2>${props.text}</h2>`;
            if (level === 3) return html`<h3>${props.text}</h3>`;
            return html`<h4>${props.text}</h4>`;
          case 'Text':
            const variant = props.variant;
            if (variant === 'h3') return html`<h3>${props.text}</h3>`;
            if (variant === 'h4') return html`<h4>${props.text}</h4>`;
            return html`<p>${props.text}</p>`;
          case 'List':
            const listItems = props.items || [];
            return html`
              <ul>
                ${listItems.map((li: string) => html`<li>${li}</li>`)}
              </ul>
            `;
          case 'Column':
            return html`
              <div class="column">
                ${children.map((childId: string) => renderComponent(childId))}
              </div>
            `;
          default:
            return html`<div class="error">Unknown component: ${type}</div>`;
        }
      } catch (e: any) {
        return html`<div class="error">Error rendering ${id}: ${e.message}</div>`;
      }
    };

    const rootItem = componentMap.get('root') || components[0];
    if (!rootItem) return html``;

    return html`
      <div class="a2ui-surface">
        ${renderComponent(rootItem.id)}
      </div>
    `;
  }
}

customElements.define('a2ui-lit-surface', A2uiLitSurface);
