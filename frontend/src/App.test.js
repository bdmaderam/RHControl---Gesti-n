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