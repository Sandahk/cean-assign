import React, { useEffect, useState } from 'react';

const API = "http://localhost:8000";

type Product = {
  id: number;
  name: string;
  price: number;
  has_colors: boolean;
  colors?: string[];
  is_kit: boolean;
  kit_components?: number[];
};

type QuoteItem = {
  product_id: number;
  quantity: number;
  color?: string;
  kit_order?: number[];
};

function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [customer, setCustomer] = useState("");
  const [items, setItems] = useState<QuoteItem[]>([]);
  const [createdQuote, setCreatedQuote] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/products`).then(res => res.json()).then(setProducts);
  }, []);

  const addToQuote = (prod: Product) => {
    const quantity = 1;
    const item: QuoteItem = { product_id: prod.id, quantity };
    if (prod.has_colors && prod.colors && prod.colors.length) {
      item.color = prod.colors[0];
    }
    if (prod.is_kit && prod.kit_components) {
      item.kit_order = [...prod.kit_components];
    }
    setItems([...items, item]);
  };

  const updateColor = (idx: number, color: string) => {
    const newItems = [...items];
    newItems[idx].color = color;
    setItems(newItems);
  };

  const reorderKit = (idx: number) => {
    const newItems = [...items];
    if (newItems[idx].kit_order) {
      newItems[idx].kit_order = newItems[idx].kit_order!.reverse();
    }
    setItems(newItems);
  };

  const submitQuote = async () => {
    const res = await fetch(`${API}/quotes`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ customer, items }),
    });
    const data = await res.json();
    if (data.id) {
      fetch(`${API}/quotes/${data.id}`)
        .then(res => res.json())
        .then(setCreatedQuote);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h2>Products</h2>
      {products.map(p => (
        <div key={p.id} style={{ borderBottom: '1px solid #ccc', padding: 8 }}>
          <strong>{p.name}</strong> (€{p.price}){' '}
          {p.has_colors && p.colors?.length > 0 &&
            <span>Colors: {p.colors.join(', ')}</span>}
          {p.is_kit && <span> (Kit)</span>}
          <button style={{ marginLeft: 8 }} onClick={() => addToQuote(p)}>Add</button>
        </div>
      ))}

      <h2>Create Quote</h2>
      <input
        type="text"
        placeholder="Customer Name"
        value={customer}
        onChange={e => setCustomer(e.target.value)}
        style={{ marginBottom: 8, width: "100%" }}
      />

      <div>
        {items.map((item, idx) => {
          const prod = products.find(p => p.id === item.product_id);
          if (!prod) return null;
          return (
            <div key={idx} style={{ marginBottom: 8, border: '1px solid #eee', padding: 6 }}>
              <span>{prod.name} x {item.quantity} </span>
              {prod.has_colors && prod.colors &&
                <select value={item.color} onChange={e => updateColor(idx, e.target.value)}>
                  {prod.colors.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              }
              {prod.is_kit && prod.kit_components &&
                <button onClick={() => reorderKit(idx)} style={{marginLeft: 8}}>
                  Reverse Kit Order
                </button>
              }
            </div>
          );
        })}
      </div>

      <button style={{ marginTop: 16 }} onClick={submitQuote}>Create Quote</button>

      {createdQuote && (
        <div style={{ marginTop: 24 }}>
          <h3>Quote Created</h3>
          <div>Customer: {createdQuote.customer}</div>
          <div>Total: €{createdQuote.total}</div>
          <ul>
            {createdQuote.items.map((it: any, i: number) =>
              <li key={i}>
                {it.product_name} x {it.quantity}
                {it.color && <> (Color: {it.color})</>}
                {it.is_kit_component && <> (Kit item, Order: {it.order})</>}
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
