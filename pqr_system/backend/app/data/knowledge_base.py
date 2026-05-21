"""
Default Knowledge Base for the PQR System.

Contains Colombian regulations, internal policies, and historical response templates
that are loaded into ChromaDB at application startup for RAG retrieval.
"""
from typing import List, Dict, Any

DEFAULT_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    # === NORMATIVA COLOMBIANA ===
    {
        "id": "ley_1437_2011_art14",
        "content": """Ley 1437 de 2011 - Código de Procedimiento Administrativo y de lo Contencioso Administrativo (CPACA)
Artículo 14. Términos para resolver. Las peticiones serán resueltas dentro de los quince (15) días hábiles siguientes a su recepción. Cuando la petición sea de información, se resolverá dentro de los diez (10) días hábiles siguientes. Si se trata de consultas, el término será de treinta (30) días hábiles. En todo caso, si dentro del término respectivo no se ha dado respuesta a la petición, se entenderá que esta fue resuelta en sentido negativo.""",
        "metadata": {"source": "Ley 1437/2011 CPACA", "type": "normativa", "category": "términos"}
    },
    {
        "id": "ley_1437_2011_art21",
        "content": """Ley 1437 de 2011 - CPACA
Artículo 21. Petición de información. Las entidades públicas deberán suministrar información a cualquier persona que la solicite, siempre que no se trate de información clasificada o reservada. El término para entregar la información será de diez (10) días hábiles contados a partir de la recepción de la petición. La información se suministrará en la forma que el peticionario la haya solicitado, si fuere posible.""",
        "metadata": {"source": "Ley 1437/2011 CPACA", "type": "normativa", "category": "petición_información"}
    },
    {
        "id": "ley_1437_2011_art23",
        "content": """Ley 1437 de 2011 - CPACA
Artículo 23. Desistimiento. El peticionario podrá desistir en cualquier momento de sus peticiones, pero las autoridades podrán continuar de oficio la actuación si lo consideran necesario por razones de interés público. El desistimiento deberá formularse expresamente.""",
        "metadata": {"source": "Ley 1437/2011 CPACA", "type": "normativa", "category": "desistimiento"}
    },
    {
        "id": "ley_1755_2015_art6",
        "content": """Ley 1755 de 2015 - Ley de Transparencia y del Derecho de Acceso a la Información Pública
Artículo 6. Solicitud de información. Toda persona tiene derecho a solicitar y recibir información de cualquier entidad pública. La entidad deberá entregar la información solicitada dentro de los diez (10) días hábiles siguientes a la recepción de la petición. Si la información no puede entregarse en este término, se deberá informar al solicitante la razón de la demora y la fecha en que se entregará.""",
        "metadata": {"source": "Ley 1755/2015", "type": "normativa", "category": "transparencia"}
    },
    {
        "id": "ley_850_2003_art33",
        "content": """Ley 850 de 2003 - Estatuto del Consumidor
Artículo 33. Reclamos. El consumidor podrá formular reclamo ante el productor o proveedor cuando considere que el producto o servicio no corresponde a las condiciones de calidad, idoneidad o seguridad ofrecidas. El reclamo deberá ser resuelto dentro de los quince (15) días hábiles siguientes a su recepción.""",
        "metadata": {"source": "Ley 850/2003", "type": "normativa", "category": "reclamo_consumidor"}
    },
    {
        "id": "decreto_2150_1995",
        "content": """Decreto 2150 de 1995 - Simplificación de trámites
Establece la simplificación de trámites y procedimientos administrativos. Las entidades públicas deberán simplificar sus trámites, eliminar requisitos innecesarios y utilizar medios electrónicos para facilitar la gestión de los ciudadanos. Los formularios deben ser sencillos y solicitar únicamente la información estrictamente necesaria.""",
        "metadata": {"source": "Decreto 2150/1995", "type": "normativa", "category": "trámites"}
    },

    # === POLÍTICAS INTERNAS ===
    {
        "id": "politica_pqr_interno",
        "content": """Política Interna de Atención de PQRs
1. Todo PQR debe ser radicado dentro de los 2 días hábiles siguientes a su recepción.
2. El área competente debe ser asignada automáticamente según el tema del PQR.
3. Las quejas sobre servicio de acueducto se asignan a Servicios Públicos.
4. Los reclamos sobre cobros indebidos se asignan a Tesorería.
5. Las peticiones de información general se asignan a Atención al Ciudadano.
6. Las solicitudes que involucren temas jurídicos se asignan a la Oficina Jurídica.
7. Todo PQR debe tener notificación al ciudadano sobre su recepción dentro de las 24 horas siguientes.
8. La respuesta final debe ser revisada por un profesional antes del envío.""",
        "metadata": {"source": "Política Interna", "type": "política", "category": "atención_pqr"}
    },
    {
        "id": "politica_servicios_publicos",
        "content": """Procedimiento para Quejas y Reclamos de Servicios Públicos
1. Verificar que el servicio esté dentro del perímetro urbano o rural de la entidad.
2. Para quejas por calidad del servicio: solicitar informe técnico al operador.
3. Para reclamos por cobro excesivo: solicitar historial de consumos y facturación.
4. Término de respuesta: 15 días hábiles conforme al CPACA.
5. Si el reclamo procede, ordenar ajuste en la facturación siguiente.
6. Si no procede, informar al ciudadano con justificación y recursos disponibles.
7. Remitir a la Superintendencia de Servicios Públicos Domiciliarios si es de su competencia.""",
        "metadata": {"source": "Política Interna", "type": "procedimiento", "category": "servicios_públicos"}
    },
    {
        "id": "politica_notificacion",
        "content": """Procedimiento de Notificación a Ciudadanos
1. La notificación de la respuesta se realizará preferentemente al correo electrónico registrado.
2. Si no hay correo electrónico, se enviará notificación física a la dirección registrada.
3. La notificación debe incluir: texto íntegro de la decisión, recursos disponibles, término para interponer recursos.
4. Contra las decisiones de la entidad procede el recurso de reposición y/o apelación.
5. Término para interponer recursos: 5 días hábiles desde la notificación.
6. La notificación se entenderá surtida 3 días después del envío por correo electrónico.""",
        "metadata": {"source": "Política Interna", "type": "procedimiento", "category": "notificación"}
    },

    # === RESPUESTAS HISTÓRICAS ===
    {
        "id": "respuesta_peticion_info_servicios",
        "content": """Respuesta histórica - Petición de Información sobre Servicios Públicos
Señor(a) ciudadano, en atención a su petición de información sobre los servicios públicos domiciliarios que presta nuestra entidad, nos permitimos informarle:
1. Los servicios de acueducto, alcantarillado y aseo son prestados directamente por la entidad.
2. Las tarifas vigentes pueden consultarse en nuestra página web o en las oficinas de atención.
3. Los horarios de atención son de lunes a viernes de 7:00 a.m. a 5:00 p.m.
4. Para reportar novedades o emergencias, comuníquese con la línea gratuita 01 8000 XXX XXX.
Fundamento legal: Artículos 14 y 21 de la Ley 1437 de 2011 (CPACA).""",
        "metadata": {"source": "Respuestas Históricas", "type": "respuesta", "category": "petición_información"}
    },
    {
        "id": "respuesta_queja_servicio",
        "content": """Respuesta histórica - Queja sobre Servicio de Atención
Señor(a) ciudadano, respecto a su queja sobre el servicio de atención recibido, le informamos:
1. Hemos dado traslado a la dependencia correspondiente para la verificación de los hechos.
2. Se realizará investigación interna sobre el personal involucrado.
3. Se adoptarán las medidas correctivas pertinentes según nuestros manuales de funciones.
4. Los resultados de la investigación serán comunicados oportunamente.
5. Agradecemos su participación ciudadana que contribuye al mejoramiento de nuestros servicios.
Fundamento legal: Artículo 14 Ley 1437/2011 y Política Interna de Atención de PQRs.""",
        "metadata": {"source": "Respuestas Históricas", "type": "respuesta", "category": "queja_servicio"}
    },
    {
        "id": "respuesta_reclamo_cobro",
        "content": """Respuesta histórica - Reclamo por Cobro Indebido
Señor(a) ciudadano, en relación con su reclamo por cobro indebido en la factura de servicios públicos, nos permitimos informarle:
1. Se verificó el historial de consumos y la facturación del periodo reclamado.
2. Se constató que [procede/no procede] el ajuste solicitado.
3. En caso de proceder: Se ordenó el ajuste en la facturación del próximo periodo.
4. En caso de no proceder: Se adjunta detalle del consumo y justificación del cobro.
5. Recurso: Contra esta decisión procede el recurso de reposición dentro de los 5 días hábiles siguientes a la notificación.
Fundamento legal: Artículos 14 y 33 Ley 1437/2011, Ley 850/2003.""",
        "metadata": {"source": "Respuestas Históricas", "type": "respuesta", "category": "reclamo_cobro"}
    },
    {
        "id": "respuesta_sugerencia_mejora",
        "content": """Respuesta histórica - Sugerencia de Mejora
Señor(a) ciudadano, agradecemos su interés en contribuir al mejoramiento de nuestra entidad. Su sugerencia ha sido evaluada y:
1. Ha sido remitida al área competente para su análisis y consideración.
2. Las sugerencias ciudadanas son insumos valiosos para el Plan de Mejoramiento Institucional.
3. Será tenida en cuenta en los procesos de planeación estratégica de la entidad.
4. Agradecemos su participación cívica y lo invitamos a seguir contribuyendo.
Fundamento legal: Artículo 14 Ley 1437/2011, Decreto 2150/1995.""",
        "metadata": {"source": "Respuestas Históricas", "type": "respuesta", "category": "sugerencia"}
    },

    # === PREGUNTAS FRECUENTES ===
    {
        "id": "faq_radicacion",
        "content": """Preguntas Frecuentes - Radicación de PQRs
¿Qué es un radicado? Es el número único que identifica su solicitud dentro del sistema.
¿Cómo puedo consultar el estado de mi PQR? Puede consultar en línea con su número de radicado o llamar a nuestra línea de atención.
¿Cuánto tiempo tarda la respuesta? Depende del tipo: Peticiones de información: 10 días hábiles. Peticiones generales: 15 días hábiles. Consultas: 30 días hábiles. Quejas y Reclamos: 15 días hábiles.
¿Puedo adjuntar soportes? Sí, puede adjuntar documentos en formato PDF, JPG o PNG hasta 10MB.
¿Qué pasa si no estoy de acuerdo con la respuesta? Puede interponer recurso de reposición dentro de los 5 días hábiles siguientes a la notificación.""",
        "metadata": {"source": "FAQ", "type": "faq", "category": "radicación"}
    },
    {
        "id": "faq_servicios_publicos",
        "content": """Preguntas Frecuentes - Servicios Públicos
¿Cómo reporto una fuga de agua? Comuníquese con la línea de emergencias 01 8000 XXX XXX o reporte en línea.
¿Por qué mi factura es tan alta? Puede deberse a consumo elevado, fugas internas, o cambios en la tarifa. Solicite verificación de consumo.
¿Cómo solicito una nueva conexión? Presente petición de conexión con copia de cédula, certificado de tradición y plano del predio.
¿Puedo solicitar suspensión temporal del servicio? Sí, presente petición indicando el periodo de suspensión deseado.""",
        "metadata": {"source": "FAQ", "type": "faq", "category": "servicios_públicos"}
    },
    {
        "id": "faq_tramites_generales",
        "content": """Preguntas Frecuentes - Trámites Generales
¿Qué documentos necesito para radicar un PQR? Necesita documento de identidad, dirección de notificación y descripción clara de su solicitud.
¿Puedo radicar un PQR en nombre de otra persona? Sí, con poder debidamente otorgado o autorización escrita.
¿El PQR es gratuito? Sí, la radicación de PQRs es gratuita conforme a la ley.
¿Puedo radicar electrónicamente? Sí, a través de nuestro portal web o correo electrónico institucional.
¿Qué hago si no me responden en el término legal? Puede acudir a la Defensoría del Pueblo o interponer acción de tutela por violación al derecho de petición.""",
        "metadata": {"source": "FAQ", "type": "faq", "category": "trámites"}
    },
]