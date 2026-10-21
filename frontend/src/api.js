const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
async function request(path, options={}) {
  const response=await fetch(`${API_URL}${path}`, {headers:{'Content-Type':'application/json', ...(options.headers||{})}, ...options});
  if (!response.ok) { let data={}; try { data=await response.json(); } catch {} throw new Error(data.detail || data.mensaje || `Error HTTP ${response.status}`); }
  if (response.status===204) return null; return response.json();
}
export const api={
 login:(data)=>request('/auth/login',{method:'POST',body:JSON.stringify(data)}),
 empleados:{list:(params='')=>request(`/empleados${params}`),get:(id)=>request(`/empleados/${id}`),create:(data)=>request('/empleados',{method:'POST',body:JSON.stringify(data)}),update:(id,data)=>request(`/empleados/${id}`,{method:'PUT',body:JSON.stringify(data)}),remove:(id)=>request(`/empleados/${id}`,{method:'DELETE'})},
 anotaciones:{list:()=>request('/anotaciones'),byEmpleado:(id)=>request(`/anotaciones/empleado/${id}`),create:(id,data)=>request(`/anotaciones/empleado/${id}`,{method:'POST',body:JSON.stringify(data)}),update:(id,data)=>request(`/anotaciones/${id}`,{method:'PUT',body:JSON.stringify(data)}),remove:(id)=>request(`/anotaciones/${id}`,{method:'DELETE'})},
 salud:()=>request('/salud')
};
export {API_URL};
