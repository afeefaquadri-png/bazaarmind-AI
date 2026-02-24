/**
 * DynamicProductForm - Renders product form fields dynamically based on shop type template.
 * This is the core of the multi-shop customization system.
 */
import { useState, useEffect } from 'react'

const FIELD_COMPONENTS = {
  text: ({ field, value, onChange }) => (
    <input
      type="text"
      className="input"
      placeholder={`Enter ${field.label.toLowerCase()}`}
      value={value || ''}
      onChange={e => onChange(field.key, e.target.value)}
    />
  ),
  number: ({ field, value, onChange }) => (
    <input
      type="number"
      className="input"
      placeholder="0"
      value={value || ''}
      onChange={e => onChange(field.key, e.target.value)}
    />
  ),
  date: ({ field, value, onChange }) => (
    <input
      type="date"
      className="input"
      value={value || ''}
      onChange={e => onChange(field.key, e.target.value)}
    />
  ),
  select: ({ field, value, onChange }) => (
    <select
      className="input"
      value={value || ''}
      onChange={e => onChange(field.key, e.target.value)}
    >
      <option value="">Select {field.label}</option>
      {(field.options || []).map(opt => (
        <option key={opt} value={opt}>{opt}</option>
      ))}
    </select>
  ),
}

export default function DynamicProductForm({ template, value = {}, onChange, errors = {} }) {
  const attributes = template?.attributes || []

  const handleChange = (key, val) => {
    onChange({ ...value, [key]: val })
  }

  if (!attributes.length) return null

  return (
    <div>
      <div className="mb-3 flex items-center gap-2">
        <span className="text-base">{template?.icon}</span>
        <p className="text-sm font-semibold text-surface-700">{template?.label} Attributes</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {attributes.map(field => {
          const Component = FIELD_COMPONENTS[field.type] || FIELD_COMPONENTS.text
          return (
            <div key={field.key} className={field.type === 'text' && !field.options ? '' : ''}>
              <label className="label">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <Component field={field} value={value[field.key]} onChange={handleChange} />
              {errors[field.key] && (
                <p className="text-red-500 text-xs mt-1">{errors[field.key]}</p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

/** Validate product attributes against template */
export function validateAttributes(attributes, template) {
  const errors = {}
  for (const field of template?.attributes || []) {
    if (field.required && !attributes[field.key]) {
      errors[field.key] = `${field.label} is required`
    }
  }
  return errors
}
