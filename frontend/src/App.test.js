import React from 'react';
import {render, screen, waitFor, fireEvent} from '@testing-library/react';
import App from './App';
import {api} from './api';

// Se simula la API para probar la interfaz sin backend.
jest.mock('./api', () => ({
  api: {
    login: jest.fn(),
    empleados: {list: jest.fn(), get: jest.fn(), create: jest.fn(), update: jest.fn(), remove: jest.fn()},
    anotaciones: {list: jest.fn(), get: jest.fn(), byEmpleado: jest.fn(), create: jest.fn(), update: jest.fn(), remove: jest.fn()},
    salud: jest.fn(),
  },
  API_URL: 'http://localhost:8000/api',
}));

const empleadosDePrueba = [
  {id: 1, nombres: 'Juan', apellidos: 'Pérez', tipo_documento: 'CC', numero_documento: '123456789', cargo: 'Desarrollador', dependencia: 'Tecnología', activo: true},
  {id: 2, nombres: 'María', apellidos: 'Gómez', tipo_documento: 'CC', numero_documento: '987654321', cargo: 'Diseñadora', dependencia: 'Marketing', activo: true},
];

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
  window.history.pushState({}, '', '/');
  api.empleados.list.mockResolvedValue([]);
  api.anotaciones.list.mockResolvedValue([]);
});

describe('Inicio de sesión', () => {
  test('con credenciales correctas guarda el token y entra al panel', async () => {
    api.login.mockResolvedValue({access_token: 'token-de-prueba', usuario: 'admin', nombre: 'Administrador RH'});
    render(<App />);

    fireEvent.click(screen.getByRole('button', {name: /iniciar sesión/i}));

    expect(await screen.findByText(/Hola, Administrador RH/i)).toBeInTheDocument();
    expect(localStorage.getItem('token')).toBe('token-de-prueba');
    expect(api.login).toHaveBeenCalledWith({usuario: 'admin', contraseña: 'admin123'});
  });

  test('con credenciales incorrectas muestra el error y no guarda sesión', async () => {
    api.login.mockRejectedValue(new Error('Usuario o contraseña incorrectos'));
    render(<App />);

    fireEvent.click(screen.getByRole('button', {name: /iniciar sesión/i}));

    expect(await screen.findByText(/Usuario o contraseña incorrectos/i)).toBeInTheDocument();
    expect(localStorage.getItem('token')).toBeNull();
    expect(screen.getByText(/Bienvenido a RHControl/i)).toBeInTheDocument();
  });
});

describe('Rutas protegidas', () => {
  test('sin sesión, /empleados redirige al inicio de sesión', async () => {
    window.history.pushState({}, '', '/empleados');
    render(<App />);

    expect(await screen.findByText(/Bienvenido a RHControl/i)).toBeInTheDocument();
    expect(api.empleados.list).not.toHaveBeenCalled();
  });
});

describe('Listado de empleados', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'token-de-prueba');
    window.history.pushState({}, '', '/empleados');
  });

  test('muestra los empleados que devuelve la API', async () => {
    api.empleados.list.mockResolvedValue(empleadosDePrueba);
    render(<App />);

    expect(await screen.findByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('María Gómez')).toBeInTheDocument();
    expect(screen.getByText('Desarrollador')).toBeInTheDocument();
  });

  test('muestra un mensaje cuando no hay empleados', async () => {
    api.empleados.list.mockResolvedValue([]);
    render(<App />);

    expect(await screen.findByText(/No se encontraron empleados/i)).toBeInTheDocument();
  });

  test('muestra el error si la API falla', async () => {
    api.empleados.list.mockRejectedValue(new Error('No se pudo conectar con el servidor.'));
    render(<App />);

    await waitFor(() => expect(screen.getByText(/No se pudo conectar con el servidor/i)).toBeInTheDocument());
  });
});
describe('Revisor de calidad de anotaciones', () => {
  test('revisa la anotación y muestra puntaje, problemas y sugerencias', async () => {
    localStorage.setItem('token', 'token-de-prueba');
    window.history.pushState({}, '', '/empleados/1/anotaciones/nueva');
    api.empleados.get.mockResolvedValue(empleadosDePrueba[0]);
    api.ia = {revisar: jest.fn().mockResolvedValue({
      puntaje: 56, nivel: 'requiere_correccion', etiqueta: 'Requiere corrección', resumen: 'Se encontraron 1 error(es).',
      hallazgos: [{regla: 'L01', categoria: 'Lenguaje', severidad: 'error', mensaje: 'El texto contiene lenguaje ofensivo.',
        sugerencia: 'Elimina los insultos.', evidencia: ['imbecil']}],
      cumplidas: ['Es legible'], reglas_evaluadas: 10, contexto: {}})};
    render(<App />);

    const descripcion = await screen.findByLabelText(/descripción/i);
    fireEvent.change(descripcion, {target: {value: 'Es un imbécil'}});
    fireEvent.click(screen.getByRole('button', {name: /revisar calidad/i}));

    expect(await screen.findByText('56/100')).toBeInTheDocument();
    expect(screen.getByText(/lenguaje ofensivo/i)).toBeInTheDocument();
    expect(screen.getByText(/elimina los insultos/i)).toBeInTheDocument();
    expect(api.ia.revisar).toHaveBeenCalledWith(expect.objectContaining({descripcion: 'Es un imbécil', tipo: 'Llamado de atención', empleado_id: 1}));
  });

  test('muestra el error si la revisión falla', async () => {
    localStorage.setItem('token', 'token-de-prueba');
    window.history.pushState({}, '', '/empleados/1/anotaciones/nueva');
    api.empleados.get.mockResolvedValue(empleadosDePrueba[0]);
    api.ia = {revisar: jest.fn().mockRejectedValue(new Error('Servicio no disponible'))};
    render(<App />);
    fireEvent.change(await screen.findByLabelText(/descripción/i), {target: {value: 'Texto de prueba'}});
    fireEvent.click(screen.getByRole('button', {name: /revisar calidad/i}));
    expect(await screen.findByText(/servicio no disponible/i)).toBeInTheDocument();
  });
});

describe('Temas y reincidencia', () => {
  test('el panel de revisión muestra los temas y la alerta de reincidencia', async () => {
    localStorage.setItem('token', 'token-de-prueba');
    window.history.pushState({}, '', '/empleados/1/anotaciones/nueva');
    api.empleados.get.mockResolvedValue(empleadosDePrueba[0]);
    api.ia = {revisar: jest.fn().mockResolvedValue({
      puntaje: 80, nivel: 'mejorable', etiqueta: 'Mejorable', resumen: 'x', hallazgos: [], cumplidas: [],
      temas: [{tema: 'puntualidad', nombre: 'Puntualidad', tono: 'negativo', evidencia: ['llego tarde']}],
      reincidencias: [{tema: 'puntualidad', nombre: 'Puntualidad', ocurrencias: 2, nivel: 'se_repite',
        mensaje: "'Puntualidad' aparece por 2.ª vez en los últimos 90 días.", fechas_previas: ['2026-11-10']}]})};
    render(<App />);
    fireEvent.change(await screen.findByLabelText(/descripción/i), {target: {value: 'Llegó tarde'}});
    fireEvent.click(screen.getByRole('button', {name: /revisar calidad/i}));
    expect(await screen.findByRole('alert')).toHaveTextContent(/2\.ª vez/);
    expect(screen.getByTitle(/llego tarde/i)).toHaveTextContent('Puntualidad');
  });

  test('el detalle del empleado muestra los temas repetidos', async () => {
    localStorage.setItem('token', 'token-de-prueba');
    window.history.pushState({}, '', '/empleados/1');
    api.empleados.get.mockResolvedValue(empleadosDePrueba[0]);
    api.anotaciones.byEmpleado.mockResolvedValue([]);
    api.ia = {temasEmpleado: jest.fn().mockResolvedValue({
      ventana_dias: 90, anotaciones: 2,
      temas: [{tema: 'puntualidad', nombre: 'Puntualidad', negativas: 2, positivas: 0, neutras: 0}],
      alertas: [{tema: 'puntualidad', nombre: 'Puntualidad', ocurrencias: 2, nivel: 'se_repite'}]})};
    render(<App />);
    expect(await screen.findByText(/temas y reincidencia/i)).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent(/2 anotaciones negativas/);
  });
});
