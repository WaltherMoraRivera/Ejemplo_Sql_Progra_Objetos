"""Seed the database using the app repositories according to the user's list of INSERTs.
This script uses the project's repository classes and domain models to insert rows in the
correct order so foreign keys line up.
"""
from pathlib import Path
from datetime import date, timedelta
import traceback

from app.infrastructure.database.oracle_connection import OracleConnection
from app.infrastructure.repositories.ciudad_repository import CiudadRepository
from app.infrastructure.repositories.sede_repository import SedeRepository
from app.infrastructure.repositories.pelicula_repository import PeliculaRepository
from app.infrastructure.repositories.funcion_repository import FuncionRepository
from app.infrastructure.repositories.proyeccion_repository import ProyeccionRepository
from app.infrastructure.repositories.asistente_repository import AsistenteRepository
from app.infrastructure.repositories.asistencia_repository import AsistenciaRepository
from app.infrastructure.repositories.jurado_repository import JuradoRepository
from app.infrastructure.repositories.participacion_jurado_repository import ParticipacionJuradoRepository
from app.infrastructure.repositories.evaluacion_repository import EvaluacionRepository
from app.infrastructure.repositories.premiacion_repository import PremiacionRepository

# domain models
from app.domain.models.ciudad import Ciudad
from app.domain.models.sede import Sede
from app.domain.models.pelicula import Pelicula
from app.domain.models.funcion import Funcion
from app.domain.models.proyeccion import Proyeccion
from app.domain.models.asistente import Asistente
from app.domain.models.asistencia import Asistencia
from app.domain.models.jurado import Jurado
from app.domain.models.participacion_jurado import ParticipacionJurado
from app.domain.models.evaluacion import Evaluacion
from app.domain.models.premiacion import Premiacion


def _add_and_get_id(repo, add_fn_name, obj, id_attr_names):
    """Call repo.add and try to determine the new id using multiple heuristics."""
    try:
        add_fn = getattr(repo, add_fn_name)
    except Exception:
        # try generic 'add' name
        add_fn = getattr(repo, 'add')
    res = add_fn(obj)
    # direct integer return
    if isinstance(res, int):
        return res
    # if tuple like (id,) or (True, id), try to pick the id
    if isinstance(res, (tuple, list)) and res:
        for v in res:
            if isinstance(v, int):
                return v
    # If True or None returned, try to find id from last element
    try:
        all_items = repo.get_all()
        if not all_items:
            return None
        last = all_items[-1]
        for attr in id_attr_names:
            if hasattr(last, attr):
                return getattr(last, attr)
    except Exception:
        pass
    return None


def main():
    settings = Path('config/settings.json')
    conn = OracleConnection.from_settings(settings)

    ciudad_repo = CiudadRepository(conn)
    sede_repo = SedeRepository(conn)
    pelicula_repo = PeliculaRepository(conn)
    funcion_repo = FuncionRepository(conn)
    proyeccion_repo = ProyeccionRepository(conn)
    asistente_repo = AsistenteRepository(conn)
    asistencia_repo = AsistenciaRepository(conn)
    jurado_repo = JuradoRepository(conn)
    participacion_repo = ParticipacionJuradoRepository(conn)
    evaluacion_repo = EvaluacionRepository(conn)
    premiacion_repo = PremiacionRepository(conn)

    try:
        print('1) Inserting Ciudades...')
        ciudades_data = [
            ('Santiago', 'Metropolitana', 'Chile'),
            ('Valparaíso', 'Valparaíso', 'Chile'),
            ('Concepción', 'Biobío', 'Chile'),
            ('Buenos Aires', 'CABA', 'Argentina'),
            ('Lima', 'Lima Metropolitana', 'Perú'),
        ]
        ciudad_ids = []
        existing_ciudades = ciudad_repo.get_all()
        for name, region, pais in ciudades_data:
            # check existing by nombre+region
            found = None
            for c in existing_ciudades:
                if getattr(c, 'nombre', None) == name and getattr(c, 'region', None) == region:
                    found = getattr(c, 'id', None) or getattr(c, 'id_ciudad', None)
                    break
            if found:
                print('Ciudad exists, skipping insert:', name, '-> id', found)
                ciudad_ids.append(found)
                continue
            cid = Ciudad(id=None, nombre=name, region=region, pais=pais, observaciones='Sin observaciones')
            new_id = _add_and_get_id(ciudad_repo, 'add', cid, ['id', 'id_ciudad'])
            print('Inserted Ciudad', name, '-> id', new_id)
            ciudad_ids.append(new_id)

        print('\n2) Inserting Sedes...')
        sedes_data = [
            ('Cine Arte Alameda', 'Av. Libertador 123', 300, 'Cine convencional', ciudad_ids[0]),
            ('Teatro Municipal Valpo', 'Calle Bellavista 456', 500, 'Teatro', ciudad_ids[1]),
            ('Cine Biobío', 'Av. Los Carrera 789', 250, 'Cine independiente', ciudad_ids[2]),
            ('Cine Gaumont', 'Av. Rivadavia 321', 400, 'Cine histórico', ciudad_ids[3]),
            ('Cine UVK', 'Av. Benavides 654', 350, 'Cine comercial', ciudad_ids[4]),
        ]
        sede_ids = []
        existing_sedes = sede_repo.get_all()
        for nombre, direccion, capacidad, tipo_sede, id_ciudad in sedes_data:
            # check existing by nombre + id_ciudad
            found = None
            for s in existing_sedes:
                if getattr(s, 'nombre', None) == nombre and getattr(s, 'id_ciudad', None) == id_ciudad:
                    found = getattr(s, 'id', None) or getattr(s, 'id_sede', None)
                    break
            if found:
                print('Sede exists, skipping insert:', nombre, '-> id', found)
                sede_ids.append(found)
                continue
            s = Sede(id=None, nombre=nombre, direccion=direccion, capacidad_maxima=capacidad, tipo_sede=tipo_sede, id_ciudad=id_ciudad, estado='Activa')
            new_id = _add_and_get_id(sede_repo, 'add', s, ['id', 'id_sede'])
            print('Inserted Sede', nombre, '-> id', new_id)
            sede_ids.append(new_id)

        print('\n3) Inserting Peliculas...')
        peliculas_data = [
            ('El Viaje', 'Chile', 'Juan Pérez', 120, 'Drama', '+14'),
            ('Sueños del Mar', 'Argentina', 'María López', 90, 'Romance', 'TE'),
            ('Luz en la Oscuridad', 'Perú', 'Carlos Ramírez', 110, 'Suspenso', '+18'),
            ('Camino al Futuro', 'Chile', 'Ana Torres', 100, 'Ciencia Ficción', '+7'),
            ('Risas Eternas', 'México', 'Pedro Sánchez', 95, 'Comedia', 'TE'),
        ]
        pelicula_ids = []
        existing_pels = pelicula_repo.get_all()
        for titulo, pais_origen, director, duracion, genero, clasificacion in peliculas_data:
            # check existing by titulo + director
            found = None
            for pel in existing_pels:
                if getattr(pel, 'titulo', None) == titulo and getattr(pel, 'director', None) == director:
                    found = getattr(pel, 'id', None) or getattr(pel, 'id_pelicula', None)
                    break
            if found:
                print('Pelicula exists, skipping insert:', titulo, '-> id', found)
                pelicula_ids.append(found)
                continue
            p = Pelicula(id=None, titulo=titulo, pais_origen=pais_origen, director=director, duracion_minutos=duracion, genero=genero, clasificacion=clasificacion, sinopsis='Sin sinopsis disponible')
            new_id = _add_and_get_id(pelicula_repo, 'add', p, ['id', 'id_pelicula'])
            print('Inserted Pelicula', titulo, '-> id', new_id)
            pelicula_ids.append(new_id)

        print('\n4) Inserting Funciones...')
        funcion_ids = []
        existing_funcs = funcion_repo.get_all()
        for i, (sede_id) in enumerate([sid for sid in sede_ids]):
            hora_val = ['18:00','20:00','19:30','21:00','17:00'][i]
            fecha_val = date.today() + timedelta(days=i)
            f = Funcion(id=None, fecha=fecha_val, hora=hora_val, precio_entrada=[5000,6000,4500,7000,5500][i], estado_funcion='Programada', observaciones='Sin observaciones', id_sede=sede_id)
            # check existing by hora + id_sede (and optionally fecha)
            found = None
            try:
                for it in existing_funcs:
                    if getattr(it, 'hora', None) == hora_val and getattr(it, 'id_sede', None) == sede_id:
                        found = getattr(it, 'id', None) or getattr(it, 'id_funcion', None)
                        break
            except Exception:
                found = None
            if found:
                print('Funcion exists for sede', sede_id, 'hora', hora_val, '-> id', found)
                funcion_ids.append(found)
                continue

            res = funcion_repo.add(f)
            if isinstance(res, int):
                new_id = res
            else:
                # try to find the inserted funcion by matching hora and id_sede
                found2 = None
                try:
                    all_funcs = funcion_repo.get_all()
                    for it in all_funcs:
                        if getattr(it, 'hora', None) == f.hora and getattr(it, 'id_sede', None) == f.id_sede:
                            found2 = getattr(it, 'id', None) or getattr(it, 'id_funcion', None)
                    new_id = found2
                except Exception:
                    new_id = None
            print('Inserted Funcion for sede', sede_id, '-> id', new_id)
            funcion_ids.append(new_id)

        print('\n5) Inserting Proyecciones...')
        proy_ids = []
        for fid, pid in zip(funcion_ids, pelicula_ids):
            # ensure fid and pid are ints (map booleans/None to numeric ids when possible)
            try:
                map_fid = fid if isinstance(fid, int) else int(fid)
            except Exception:
                map_fid = fid
            try:
                map_pid = pid if isinstance(pid, int) else int(pid)
            except Exception:
                map_pid = pid
            # check existing
            existing_proys = proyeccion_repo.get_all()
            exists = False
            for ex in existing_proys:
                if getattr(ex, 'id_funcion', None) == map_fid and getattr(ex, 'id_pelicula', None) == map_pid:
                    print('Proyeccion exists', (map_fid, map_pid))
                    exists = True
                    break
            if exists:
                proy_ids.append((map_fid, map_pid))
                continue
            pr = Proyeccion(id_funcion=map_fid, id_pelicula=map_pid, orden_proyeccion=1, comentarios='Sin comentarios')
            added = proyeccion_repo.add(pr)
            print('Inserted Proyeccion (funcion, pelicula)=', (map_fid, map_pid), '->', added)
            proy_ids.append((map_fid, map_pid))

        print('\n6) Inserting Asistentes...')
        asistentes_data = [
            ('Pedro Gómez', 'pedro.gomez@mail.com', '9991111', 28, 'Santiago', 'General'),
            ('Laura Martínez', 'laura.martinez@mail.com', '9992222', 22, 'Valparaíso', 'Estudiante'),
            ('Carlos Ramírez', 'carlos.ramirez@mail.com', '9993333', 35, 'Concepción', 'Profesional'),
            ('Ana Torres', 'ana.torres@mail.com', '9994444', 30, 'Buenos Aires', 'Prensa'),
            ('Sofía Díaz', 'sofia.diaz@mail.com', '9995555', 26, 'Lima', 'General'),
        ]
        asistente_ids = []
        existing_asist = asistente_repo.get_all()
        for nombre, correo, telefono, edad, ciudad_res, tipo_asistente in asistentes_data:
            # check by correo
            found = None
            for ex in existing_asist:
                if getattr(ex, 'correo', None) == correo:
                    found = getattr(ex, 'id', None) or getattr(ex, 'id_asistente', None)
                    break
            if found:
                print('Asistente exists, skipping insert:', correo, '-> id', found)
                asistente_ids.append(found)
                continue
            a = Asistente(id=None, nombre=nombre, correo=correo, telefono=telefono, edad=edad, ciudad_residencia=ciudad_res, tipo_asistente=tipo_asistente)
            new_id = _add_and_get_id(asistente_repo, 'add', a, ['id', 'id_asistente'])
            print('Inserted Asistente', nombre, '-> id', new_id)
            asistente_ids.append(new_id)

        print('\n7) Inserting Asistencias...')
        asistencias_data = [
            (1,1,2,'Tarjeta'),(2,2,1,'Efectivo'),(3,3,3,'Transferencia'),(4,4,1,'Tarjeta'),(5,5,2,'Efectivo'),
            (1,2,150,'Tarjeta'),(1,3,130,'Efectivo'),(2,1,200,'Tarjeta'),(2,4,100,'Efectivo'),(3,5,60,'Transferencia'),
            (4,1,180,'Efectivo'),(4,3,100,'Tarjeta'),(5,2,180,'Transferencia'),(5,4,140,'Tarjeta')
        ]
        existing_asistencias = asistencia_repo.get_all()
        for fid, aid, entradas, metodo in asistencias_data:
            # map provided numeric ids to actual ids inserted earlier if available
            map_fid = funcion_ids[fid-1] if fid-1 < len(funcion_ids) else fid
            map_aid = asistente_ids[aid-1] if aid-1 < len(asistente_ids) else aid
            # skip if asistencia already exists (PK: id_funcion,id_asistente)
            exists = False
            for ex in existing_asistencias:
                if getattr(ex, 'id_funcion', None) == map_fid and getattr(ex, 'id_asistente', None) == map_aid:
                    exists = True
                    break
            if exists:
                print('Asistencia exists, skipping', (map_fid, map_aid))
                continue
            asis = Asistencia(id_funcion=map_fid, id_asistente=map_aid, entradas=entradas, fecha_compra=date.today(), metodo_pago=metodo, comentarios='Sin comentarios')
            try:
                added = asistencia_repo.add(asis)
                print('Inserted Asistencia (funcion,asistente)=', (map_fid, map_aid), '->', added)
            except Exception as e:
                print('ERROR inserting asistencia', (map_fid, map_aid), e)
                continue

        print('\n8) Inserting Jurados...')
        jurados_data = [
            ('Dr. Juan Herrera', 'juan.herrera@mail.com', 'Dirección', 'Chile', 10, 'Permanente'),
            ('María Vega', 'maria.vega@mail.com', 'Actuación', 'Argentina', 8, 'Invitado'),
            ('Ricardo Soto', 'ricardo.soto@mail.com', 'Guion', 'Perú', 12, 'Honorario'),
            ('Diana Fuentes', 'diana.fuentes@mail.com', 'Fotografía', 'Chile', 15, 'Permanente'),
            ('Fernando Ríos', 'fernando.rios@mail.com', 'Sonido', 'México', 20, 'Invitado'),
        ]
        jurado_ids = []
        existing_jurados = jurado_repo.get_all()
        for nombre, correo, especialidad, pais, exp, tipo in jurados_data:
            found = None
            for ex in existing_jurados:
                if getattr(ex, 'correo', None) == correo:
                    found = getattr(ex, 'id', None) or getattr(ex, 'id_jurado', None)
                    break
            if found:
                print('Jurado exists, skipping insert:', correo, '-> id', found)
                jurado_ids.append(found)
                continue
            j = Jurado(nombre=nombre, correo=correo, especialidad=especialidad, pais_origen=pais, experiencia_anos=exp, tipo_jurado=tipo, biografia='Sin biografia disponible')
            new_id = _add_and_get_id(jurado_repo, 'add', j, ['id', 'id_jurado'])
            print('Inserted Jurado', nombre, '-> id', new_id)
            jurado_ids.append(new_id)

        print('\n9) Inserting Participaciones de Jurado...')
        for jid, fid in zip(jurado_ids, funcion_ids):
            part = ParticipacionJurado(id_jurado=jid, id_funcion=fid, rol_participacion='Evaluador', comentarios='Sin comentarios')
            added = participacion_repo.add(part)
            print('Inserted Participacion', (jid, fid), '->', added)

        print('\n10) Inserting Evaluaciones...')
        for jid, pid, puntuacion, comentario, categoria in [
            (jurado_ids[0], pelicula_ids[0], 9, 'Gran dirección', 'Direccion'),
            (jurado_ids[1], pelicula_ids[1], 8, 'Buena actuación', 'Actuacion'),
            (jurado_ids[2], pelicula_ids[2], 7, 'Historia interesante', 'Guion'),
            (jurado_ids[3], pelicula_ids[3], 10, 'Fotografía impecable', 'Fotografia'),
            (jurado_ids[4], pelicula_ids[4], 9, 'Excelente sonido', 'Sonido'),
        ]:
            ev = Evaluacion(id_jurado=jid, id_pelicula=pid, puntuacion=puntuacion, comentario=comentario, fecha=date.today(), categoria_evaluada=categoria)
            added = evaluacion_repo.add(ev)
            print('Inserted Evaluacion', (jid, pid), '->', added)

        print('\n11) Inserting Premiaciones...')
        for pid, categoria, edicion, posicion, descripcion in [
            (pelicula_ids[0], 'Mejor Dirección', 2025, 1, 'Premio a la mejor dirección'),
            (pelicula_ids[1], 'Mejor Actuación', 2025, 1, 'Premio a la mejor actuación'),
            (pelicula_ids[2], 'Mejor Guion', 2025, 1, 'Premio al mejor guion'),
            (pelicula_ids[3], 'Mejor Fotografía', 2025, 1, 'Premio a la mejor fotografía'),
            (pelicula_ids[4], 'Mejor Sonido', 2025, 1, 'Premio al mejor sonido'),
        ]:
            pm = Premiacion(id_premio=None, id_pelicula=pid, categoria=categoria, edicion=edicion, posicion=posicion, descripcion=descripcion, fecha_premiacion=date.today())
            added = premiacion_repo.add(pm)
            print('Inserted Premiacion for pelicula', pid, '->', added)

        print('\nSeeding complete.')

    except Exception as e:
        print('ERROR during seeding', e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
