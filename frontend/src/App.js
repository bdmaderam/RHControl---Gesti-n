import React,{useEffect,useState} from 'react';
import {BrowserRouter,Routes,Route,Navigate,useNavigate,useParams} from 'react-router-dom';
import {api} from './api';
import './index.css';

/* ---------- Icon set (custom line icons, replaces emoji) ---------- */
const Icon=({children})=><span className="icon" aria-hidden="true">{children}</span>;
const IconAlert=()=><Icon><svg viewBox="0 0 24 24"><path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4"/><path d="M12 17h.01"/></svg></Icon>;
const IconArrowLeft=()=><Icon><svg viewBox="0 0 24 24"><path d="M19 12H5"/><path d="M11 6l-6 6 6 6"/></svg></Icon>;
const IconHome=()=><Icon><svg viewBox="0 0 24 24"><path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9h12v-9"/><path d="M10 19v-5h4v5"/></svg></Icon>;
const IconUsers=()=><Icon><svg viewBox="0 0 24 24"><path d="M8 12a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/><path d="M2 20c.6-3.8 2.9-6 6-6s5.4 2.2 6 6"/><path d="M16.5 6.5a2.8 2.8 0 1 1 0 5.6"/><path d="M15 13.3c2.6.2 4.6 2.2 5 6.7"/></svg></Icon>;
const IconReport=()=><Icon><svg viewBox="0 0 24 24"><path d="M4 20V10"/><path d="M11 20V4"/><path d="M18 20v-7"/><path d="M2 20h20"/></svg></Icon>;
const IconLogout=()=><Icon><svg viewBox="0 0 24 24"><path d="M9 4H5v16h4"/><path d="M14 8l4 4-4 4"/><path d="M18 12H9"/></svg></Icon>;
const IconCheck=()=><Icon><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m8.5 12.3 2.4 2.4 4.6-5.2"/></svg></Icon>;
const IconNote=()=><Icon><svg viewBox="0 0 24 24"><path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/><path d="M9 13h6"/><path d="M9 17h4"/></svg></Icon>;
const IconUserPlus=()=><Icon><svg viewBox="0 0 24 24"><path d="M9 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"/><path d="M2 21c.7-4.4 3.4-7 7-7s6.3 2.6 7 7"/><path d="M19 8v6"/><path d="M16 11h6"/></svg></Icon>;
const IconSearch=()=><Icon><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg></Icon>;
const IconChevronRight=()=><Icon><svg viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"/></svg></Icon>;
const IconPlus=()=><Icon><svg viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M5 12h14"/></svg></Icon>;

const initial={nombres:'',apellidos:'',tipo_documento:'CC',numero_documento:'',fecha_nacimiento:'',cargo:'',salario:0,dependencia:'',tiene_cuenta_bancaria:false,es_temporal:false,activo:true};

const Layout=({children})=>{
  const nav=useNavigate();
  return <>
    <header className="topbar">
      <div className="brand"><span className="brand-mark">RH</span>Control</div>
      <nav>
        <button onClick={()=>nav('/panel')}><IconHome/>Panel</button>
        <button onClick={()=>nav('/empleados')}><IconUsers/>Empleados</button>
        <button onClick={()=>nav('/reportes')}><IconReport/>Reportes</button>
        <button className="logout" onClick={()=>{localStorage.clear();nav('/')}}><IconLogout/>Cerrar sesión</button>
      </nav>
    </header>
    <main>{children}</main>
  </>
};

const ErrorBox=({message,onClose})=>message?<div className="alert error"><span><IconAlert/>{message}</span><button onClick={onClose}>×</button></div>:null;

function Login(){const nav=useNavigate(); const [form,setForm]=useState({usuario:'admin',contraseña:'admin123'}); const [error,setError]=useState(''); const submit=async e=>{e.preventDefault();try{const r=await api.login(form);localStorage.setItem('token',r.access_token);localStorage.setItem('nombre',r.nombre);nav('/panel')}catch(err){setError(err.message)}}; return <div className="login-page"><div className="login-card"><div className="logo-mark">RH</div><h1>Bienvenido a RHControl</h1><p>Gestión sencilla y organizada de recursos humanos.</p><ErrorBox message={error} onClose={()=>setError('')}/><form onSubmit={submit}><label>Usuario<input value={form.usuario} onChange={e=>setForm({...form,usuario:e.target.value})}/></label><label>Contraseña<input type="password" value={form.contraseña} onChange={e=>setForm({...form,contraseña:e.target.value})}/></label><button className="primary full">Iniciar sesión</button></form><small>Usuario de prueba: admin · Contraseña: admin123</small></div></div>}

function Panel(){
  const nav=useNavigate();
  const [stats,setStats]=useState({total:0,activos:0,anotaciones:0});
  useEffect(()=>{
    Promise.all([api.empleados.list(),api.anotaciones.list()])
      .then(([e,a])=>setStats({total:e.length,activos:e.filter(x=>x.activo).length,anotaciones:a.length}))
      .catch(()=>{})
  },[]);

  return <Layout>
    <div className="page">
      <section className="hero">
        <p className="eyebrow">Panel de control</p>
        <h1>Hola, {localStorage.getItem('nombre')||'Administrador'}</h1>
        <p>Administra empleados, consulta su información y registra anotaciones desde un solo lugar.</p>
      </section>

      <div className="stats">
        <div><div className="stat-icon"><IconUsers/></div><b>{stats.total}</b><small>Empleados</small></div>
        <div><div className="stat-icon"><IconCheck/></div><b>{stats.activos}</b><small>Activos</small></div>
        <div><div className="stat-icon"><IconNote/></div><b>{stats.anotaciones}</b><small>Anotaciones</small></div>
      </div>

      <h2>Acciones rápidas</h2>
      <div className="action-list card">
        <button className="action-row" onClick={()=>nav('/empleados/nuevo')}>
          <span className="action-icon"><IconUserPlus/></span>
          <span className="action-copy"><b>Agregar empleado</b><small>Registrar una nueva persona</small></span>
          <span className="action-chevron"><IconChevronRight/></span>
        </button>
        <button className="action-row" onClick={()=>nav('/empleados')}>
          <span className="action-icon"><IconSearch/></span>
          <span className="action-copy"><b>Consultar empleados</b><small>Buscar y administrar registros</small></span>
          <span className="action-chevron"><IconChevronRight/></span>
        </button>
        <button className="action-row" onClick={()=>nav('/reportes')}>
          <span className="action-icon"><IconReport/></span>
          <span className="action-copy"><b>Ver reportes</b><small>Resumen de la información</small></span>
          <span className="action-chevron"><IconChevronRight/></span>
        </button>
      </div>
    </div>
  </Layout>
}

function EmployeeForm({initialData,onSubmit,title}){const nav=useNavigate();const [form,setForm]=useState({...initial,...initialData,fecha_nacimiento:initialData?.fecha_nacimiento||''});const [error,setError]=useState('');const change=e=>{const {name,value,type,checked}=e.target;setForm({...form,[name]:type==='checkbox'?checked:value})};const submit=async e=>{e.preventDefault();setError('');try{await onSubmit({...form,salario:Number(form.salario),fecha_nacimiento:form.fecha_nacimiento||null});nav('/empleados')}catch(err){setError(err.message)}};return <div className="page narrow"><button className="back" onClick={()=>nav(-1)}><IconArrowLeft/> Regresar</button><h1>{title}</h1><p className="muted">Completa la información del empleado.</p><ErrorBox message={error} onClose={()=>setError('')}/><form className="card form-grid" onSubmit={submit}><label>Nombres*<input name="nombres" value={form.nombres} onChange={change} required/></label><label>Apellidos*<input name="apellidos" value={form.apellidos} onChange={change} required/></label><label>Tipo de documento<select name="tipo_documento" value={form.tipo_documento} onChange={change}><option>CC</option><option>CE</option><option>PA</option></select></label><label>Número de documento*<input name="numero_documento" value={form.numero_documento} onChange={change} required/></label><label>Fecha de nacimiento<input type="date" name="fecha_nacimiento" value={form.fecha_nacimiento||''} onChange={change}/></label><label>Cargo*<input name="cargo" value={form.cargo} onChange={change} required/></label><label>Salario<input type="number" min="0" name="salario" value={form.salario} onChange={change}/></label><label>Dependencia<input name="dependencia" value={form.dependencia} onChange={change}/></label><label className="check"><input type="checkbox" name="tiene_cuenta_bancaria" checked={form.tiene_cuenta_bancaria} onChange={change}/> Tiene cuenta bancaria</label><label className="check"><input type="checkbox" name="es_temporal" checked={form.es_temporal} onChange={change}/> Ingreso por temporal</label><label className="check"><input type="checkbox" name="activo" checked={form.activo} onChange={change}/> Empleado activo</label><div className="form-actions"><button type="button" className="secondary" onClick={()=>nav(-1)}>Cancelar</button><button className="primary">Guardar</button></div></form></div>}

function EmployeeList(){const nav=useNavigate();const [items,setItems]=useState([]);const [filters,setFilters]=useState({documento:'',nombre:'',activos:''});const [loading,setLoading]=useState(true);const [error,setError]=useState('');const load=async()=>{setLoading(true);try{const q=new URLSearchParams();if(filters.documento)q.set('documento',filters.documento);if(filters.nombre)q.set('nombre',filters.nombre);if(filters.activos!=='')q.set('activos',filters.activos);setItems(await api.empleados.list(q.toString()?`?${q}`:''));}catch(e){setError(e.message)}finally{setLoading(false)}};useEffect(()=>{load()},[filters]);const remove=async id=>{if(!window.confirm('¿Eliminar este empleado y sus anotaciones?'))return;try{await api.empleados.remove(id);load()}catch(e){setError(e.message)}};return <Layout><div className="page"><div className="page-head"><div><button className="back" onClick={()=>nav('/panel')}><IconArrowLeft/> Panel</button><h1>Listado de empleados</h1><p className="muted">Consulta, edita y administra los registros.</p></div><button className="primary" onClick={()=>nav('/empleados/nuevo')}><IconPlus/> Agregar empleado</button></div><ErrorBox message={error} onClose={()=>setError('')}/><div className="filter card"><input placeholder="Buscar por nombre" value={filters.nombre} onChange={e=>setFilters({...filters,nombre:e.target.value})}/><input placeholder="Número de documento" value={filters.documento} onChange={e=>setFilters({...filters,documento:e.target.value})}/><select value={filters.activos} onChange={e=>setFilters({...filters,activos:e.target.value})}><option value="">Todos</option><option value="true">Activos</option><option value="false">Inactivos</option></select></div>{loading?<div className="loading">Cargando empleados...</div>:<div className="table-wrap card"><table><thead><tr><th>Empleado</th><th>Documento</th><th>Cargo</th><th>Dependencia</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>{items.map(e=><tr key={e.id}><td><b>{e.nombres} {e.apellidos}</b></td><td>{e.tipo_documento} {e.numero_documento}</td><td>{e.cargo}</td><td>{e.dependencia||'—'}</td><td><span className={`badge ${e.activo?'active':'inactive'}`}>{e.activo?'Activo':'Inactivo'}</span></td><td className="actions"><button onClick={()=>nav(`/empleados/${e.id}`)}>Ver</button><button onClick={()=>nav(`/empleados/${e.id}/editar`)}>Editar</button><button className="danger-text" onClick={()=>remove(e.id)}>Eliminar</button></td></tr>)}</tbody></table>{!items.length&&<div className="empty">No se encontraron empleados.</div>}</div>}</div></Layout>}

function EmployeeDetail(){const nav=useNavigate();const {id}=useParams();const [emp,setEmp]=useState(null);const [notes,setNotes]=useState([]);const [error,setError]=useState('');const load=async()=>{try{const [e,n]=await Promise.all([api.empleados.get(id),api.anotaciones.byEmpleado(id)]);setEmp(e);setNotes(n)}catch(e){setError(e.message)}};useEffect(()=>{load()},[id]);const del=async nid=>{if(!window.confirm('¿Eliminar anotación?'))return;try{await api.anotaciones.remove(nid);load()}catch(e){setError(e.message)}};if(!emp)return <Layout><div className="page"><ErrorBox message={error} onClose={()=>setError('')}/><div className="loading">Cargando...</div></div></Layout>;return <Layout><div className="page"><button className="back" onClick={()=>nav('/empleados')}><IconArrowLeft/> Empleados</button><div className="detail-head"><div><p className="eyebrow">Detalle del empleado</p><h1>{emp.nombres} {emp.apellidos}</h1><p className="muted">{emp.tipo_documento} {emp.numero_documento}</p></div><div><button className="secondary" onClick={()=>nav(`/empleados/${id}/editar`)}>Editar</button> <button className="primary" onClick={()=>nav(`/empleados/${id}/anotaciones/nueva`)}><IconPlus/> Anotación</button></div></div><ErrorBox message={error} onClose={()=>setError('')}/><div className="detail-grid"><section className="card detail-card"><h2>Información laboral</h2><Info label="Cargo" value={emp.cargo}/><Info label="Dependencia" value={emp.dependencia}/><Info label="Salario" value={new Intl.NumberFormat('es-CO',{style:'currency',currency:'COP'}).format(emp.salario)}/><Info label="Estado" value={emp.activo?'Activo':'Inactivo'}/><Info label="Temporal" value={emp.es_temporal?'Sí':'No'}/><Info label="Cuenta bancaria" value={emp.tiene_cuenta_bancaria?'Sí':'No'}/></section><section className="card detail-card"><div className="section-title"><h2>Anotaciones</h2><span className="badge active">{notes.length}</span></div>{notes.length?notes.map(n=><div className="note" key={n.id}><div><b>{n.tipo}</b><small>{new Date(n.fecha+'T00:00:00').toLocaleDateString('es-CO')}</small></div><p>{n.descripcion}</p><div><button onClick={()=>nav(`/anotaciones/${n.id}/editar`)}>Editar</button><button className="danger-text" onClick={()=>del(n.id)}>Eliminar</button></div></div>):<div className="empty">Este empleado no tiene anotaciones.</div>}</section></div></div></Layout>}

const Info=({label,value})=><div className="info-row"><span>{label}</span><b>{value}</b></div>;

function NewNote(){const nav=useNavigate();const {id}=useParams();const [emp,setEmp]=useState(null);const [form,setForm]=useState({tipo:'Llamado de atención',descripcion:'',fecha:new Date().toISOString().slice(0,10)});const [error,setError]=useState('');useEffect(()=>{api.empleados.get(id).then(setEmp).catch(e=>setError(e.message))},[id]);const save=async e=>{e.preventDefault();try{await api.anotaciones.create(id,form);nav(`/empleados/${id}`)}catch(e){setError(e.message)}};return <Layout><div className="page narrow"><button className="back" onClick={()=>nav(-1)}><IconArrowLeft/> Regresar</button><h1>Nueva anotación</h1>{emp&&<p className="muted">Empleado: <b>{emp.nombres} {emp.apellidos}</b></p>}<ErrorBox message={error} onClose={()=>setError('')}/><form className="card form-stack" onSubmit={save}><label>Tipo<select value={form.tipo} onChange={e=>setForm({...form,tipo:e.target.value})}><option>Llamado de atención</option><option>Felicitación</option><option>Observación</option><option>Reconocimiento</option><option>Otro</option></select></label><label>Fecha<input type="date" value={form.fecha} onChange={e=>setForm({...form,fecha:e.target.value})} required/></label><label>Descripción<textarea rows="6" value={form.descripcion} onChange={e=>setForm({...form,descripcion:e.target.value})} required/></label><div className="form-actions"><button type="button" className="secondary" onClick={()=>nav(-1)}>Cancelar</button><button className="primary">Guardar anotación</button></div></form></div></Layout>}

function EditEmployee(){const {id}=useParams();const [emp,setEmp]=useState(null);const [error,setError]=useState('');useEffect(()=>{api.empleados.get(id).then(setEmp).catch(e=>setError(e.message))},[id]);if(!emp)return <Layout><div className="page"><ErrorBox message={error} onClose={()=>setError('')}/><div className="loading">Cargando...</div></div></Layout>;return <Layout><EmployeeForm title="Editar empleado" initialData={emp} onSubmit={data=>api.empleados.update(id,data)}/></Layout>}

function EditNote(){const nav=useNavigate();const {id}=useParams();const [note,setNote]=useState(null);const [error,setError]=useState('');useEffect(()=>{api.anotaciones.list().then(xs=>setNote(xs.find(x=>String(x.id)===String(id)))).catch(e=>setError(e.message))},[id]);if(!note)return <Layout><div className="page"><ErrorBox message={error||'Anotación no encontrada'} onClose={()=>setError('')}/></div></Layout>;const save=async e=>{e.preventDefault();try{await api.anotaciones.update(id,note);nav(`/empleados/${note.empleado_id}`)}catch(e){setError(e.message)}};return <Layout><div className="page narrow"><button className="back" onClick={()=>nav(-1)}><IconArrowLeft/> Regresar</button><h1>Editar anotación</h1><ErrorBox message={error} onClose={()=>setError('')}/><form className="card form-stack" onSubmit={save}><label>Tipo<select value={note.tipo} onChange={e=>setNote({...note,tipo:e.target.value})}><option>Llamado de atención</option><option>Felicitación</option><option>Observación</option><option>Reconocimiento</option><option>Otro</option></select></label><label>Fecha<input type="date" value={note.fecha} onChange={e=>setNote({...note,fecha:e.target.value})}/></label><label>Descripción<textarea rows="6" value={note.descripcion} onChange={e=>setNote({...note,descripcion:e.target.value})}/></label><div className="form-actions"><button type="button" className="secondary" onClick={()=>nav(-1)}>Cancelar</button><button className="primary">Actualizar</button></div></form></div></Layout>}

function Reports(){
  const [emps,setEmps]=useState([]);
  const [notes,setNotes]=useState([]);
  const nav=useNavigate();

  useEffect(()=>{
    Promise.all([
      api.empleados.list(),
      api.anotaciones.list()
    ]).then(([e,n])=>{
      setEmps(e);
      setNotes(n);
    }).catch(()=>{});
  },[]);

  const download=()=>{
    const header=[
      'ID',
      'Nombres',
      'Apellidos',
      'Documento',
      'Cargo',
      'Dependencia',
      'Salario',
      'Estado'
    ];

    const rows=emps.map(e=>[
      e.id,
      e.nombres,
      e.apellidos,
      e.numero_documento,
      e.cargo,
      e.dependencia,
      e.salario,
      e.activo?'Activo':'Inactivo'
    ]);

    const csv=[
      header,
      ...rows
    ]
      .map(r=>r.map(v=>`"${String(v??'').replaceAll('"','""')}"`).join(','))
      .join('\n');

    const blob=new Blob(
      [csv],
      {type:'text/csv;charset=utf-8;'}
    );

    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='reporte_empleados.csv';
    a.click();

    URL.revokeObjectURL(a.href);
  };

  return <Layout>
    <div className="page">
      <button className="back" onClick={()=>nav('/panel')}>
        <IconArrowLeft/> Panel
      </button>

      <h1>Reporte de empleados</h1>

      <p className="muted">
        Resumen generado directamente desde PostgreSQL mediante la API REST.
      </p>

      <div className="stats">
        <div>
          <div className="stat-icon"><IconUsers/></div>
          <b>{emps.length}</b>
          <small>Total empleados</small>
        </div>

        <div>
          <div className="stat-icon"><IconCheck/></div>
          <b>{emps.filter(e=>e.activo).length}</b>
          <small>Activos</small>
        </div>

        <div>
          <div className="stat-icon"><IconNote/></div>
          <b>{notes.length}</b>
          <small>Total anotaciones</small>
        </div>
      </div>

      <div className="card report">
        <div className="section-title">
          <h2>Resumen</h2>
          <button className="secondary" onClick={download}>
            Descargar CSV
          </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>Empleado</th>
              <th>Cargo</th>
              <th>Dependencia</th>
              <th>Estado</th>
            </tr>
          </thead>

          <tbody>
            {emps.map(e=>
              <tr key={e.id}>
                <td>{e.nombres} {e.apellidos}</td>
                <td>{e.cargo}</td>
                <td>{e.dependencia||'—'}</td>
                <td>{e.activo?'Activo':'Inactivo'}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  </Layout>
}
function Protected({children}){return localStorage.getItem('token')?<>{children}</>:<Navigate to="/" replace/>}
export default function App(){return <BrowserRouter><Routes><Route path="/" element={<Login/>}/><Route path="/panel" element={<Protected><Panel/></Protected>}/><Route path="/empleados" element={<Protected><EmployeeList/></Protected>}/><Route path="/empleados/nuevo" element={<Protected><Layout><EmployeeForm title="Agregar nuevo empleado" onSubmit={api.empleados.create}/></Layout></Protected>}/><Route path="/empleados/:id" element={<Protected><EmployeeDetail/></Protected>}/><Route path="/empleados/:id/editar" element={<Protected><EditEmployee/></Protected>}/><Route path="/empleados/:id/anotaciones/nueva" element={<Protected><NewNote/></Protected>}/><Route path="/anotaciones/:id/editar" element={<Protected><EditNote/></Protected>}/><Route path="/reportes" element={<Protected><Reports/></Protected>}/><Route path="*" element={<Navigate to="/panel" replace/>}/></Routes></BrowserRouter>}
