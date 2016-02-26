'''
Created on Feb 14, 2016

@author: Patrick
'''
#python imports
import time
import math

#blender imports
import bmesh
from mathutils import Vector, Quaternion, Matrix
from mathutils.geometry import intersect_point_line, intersect_line_line

def test_obtuse(f):
    '''
    tests if any verts have obtuse angles in a bmesh face
    if so returns True, vert_index, edge_index opposite (for splitting)
    if not, returns False, -1, -1
    
    follow notations set out here
    http://mathworld.wolfram.com/LawofCosines.html
    http://mathworld.wolfram.com/ObtuseTriangle.html
    
    internal bisector theorem
    http://www.codecogs.com/users/22109/gm_18.gif
    '''
    assert len(f.verts) == 3, "face is not a triangle: %i" % len(f.verts)
    
    
    A = f.verts[0]
    B = f.verts[1]
    C = f.verts[2]
    
    
    a = C.co - B.co  #side opposite a
    b = A.co - C.co  #side opposite b
    c = B.co - A.co  #side opposite c
    
    AA, BB, CC = a.length**2, b.length**2, c.length**2


    if AA + BB < CC:
        ob_bool = True
        cut_location = A.co + b.length/(a.length + b.length)*c
        v_ind = C.index
        e_ind = [e.index for e in f.edges if e.other_vert(A) == B][0]
        
    elif BB + CC < AA:
        ob_bool = True
        v_ind = A.index
        cut_location = B.co + c.length/(b.length + c.length)*a
        e_ind = [e.index for e in f.edges if e.other_vert(B) == C][0]
    
    elif CC + AA < BB:
        ob_bool = True
        v_ind = B.index
        cut_location = C.co + a.length/(c.length +a.length)*b
        e_ind = [e.index for e in f.edges if e.other_vert(C) == A][0]
        
        
    else:
        ob_bool, v_ind, e_ind, cut_location =  False, -1, -1, Vector((0,0,0))
    
    return ob_bool, v_ind, e_ind, cut_location 


def unwrap_tri_fan(bme, vcenter, ed_split, face_ref, max_folds = None):

    #this allows us to sort them
    
    l = vcenter.link_loops[0]
    edges = [l.edge]

    for i in range(0,len(vcenter.link_edges)-1):
        l = l.link_loop_prev.link_loop_radial_next
        if l.edge in edges:
            print('bad indexing dummy')
            continue
        edges += [l.edge]
    
    
    verts = [ed.other_vert(vcenter) for ed in edges]
    
    
    if max_folds != None:
        max_folds = min(max_folds, len(edges)-1)
    else:
        max_folds = len(edges) - 1
        
    n = edges.index(ed_split)
    edges = edges[n:] + edges[0:n]
    verts = verts[n:] + verts[0:n]
    
    reverse = -1
    
    if edges[1] not in face_ref.edges:
        edges.reverse()
        verts.reverse()
        edges = [edges[-1]] + edges[1:]
        verts = [verts[-1]] + verts[1:]
        reverse = 1
    
    for i in range(1,len(edges)-1):
        if (i + 1) > max_folds: 
            print('Maxed out on %i iterate' % i)
            print('Max folds %i' % max_folds)
            continue
        
        axis = vcenter.co - verts[i].co
        angle = edges[i].calc_face_angle_signed()
        
        if angle < 0:
            print('negative angle')
            if edges[i].verts[1] != vcenter:
                rev2 = -1
        else:
            rev2 = 1
        q = Quaternion(axis.normalized(),rev2* reverse* angle)
        for n in range(i+1,len(edges)):
            print('changing vert %i with index %i' % (n, verts[n].index))
            verts[n].co = q * (verts[n].co - verts[i].co) + verts[i].co
        
        
def test_obtuse_pts(v0,v1,v2):    
    
    a = v2 - v1  #side opposite a
    b = v0 - v2  #side opposite b
    c = v1 - v0  #side opposite c
    
    AA, BB, CC = a.length**2, b.length**2, c.length**2

    if AA + BB < CC:
        return True, 0

    elif BB + CC < AA:
        return True, 1
    
    elif CC + AA < BB:
        return True, 2
        
    else:
        return False, -1
    
def test_accute(v0,v1,v2):
    '''
    checks if angle formed by v0->v1 and v0->v2 is accute
    (the angle at v0 is acute
    '''
    a = v2 - v1  #side opposite a
    b = v0 - v2  #side opposite b
    c = v1 - v0  #side opposite c
    
    AA, BB, CC = a.length**2, b.length**2, c.length**2

    if CC + BB > AA:
        return True
    return False
    
    
def unwrap_tri_obtuse(vcenter, vobtuse, face):
    '''
    vcenter - a vertex within the wave front
    vobtuse - the obtuse vertex
    face - the face that vcenter and vobtuse share
    
    return - 
        unwrapped_position, the actual vert, j number of unwraps
        v_cos[j], verts[j], j
    '''

    if vcenter not in face.verts:
        print('vcenter not in face')
        print('v index %i, face index %i' % (vcenter.index, face.index))
        
        for v in face.verts:
            print(v.index)

        vcenter.select = True
        face.select = True
        
    if vobtuse not in face.verts:
        print('vobtuse not in face')
        print('v index %i, face index %i' % (vobtuse.index, face.index))
        vobtuse.select = True
        face.select = True
        
        for v in face.verts:
            print(v.index)
        
    ed_base = [e for e in face.edges if vcenter in e.verts and vobtuse in e.verts][0]
    ed_unfold = [e for e in face.edges if e in vcenter.link_edges and e != ed_base][0]
    
    print(ed_base.index)
    print(ed_unfold.index)
    #this allows us to sort them
    
    l = vcenter.link_loops[0]
    edges = [l.edge]

    for i in range(0,len(vcenter.link_edges)-1):
        l = l.link_loop_prev.link_loop_radial_next
        if l.edge in edges:
            print('bad indexing dummy')
            continue
        edges += [l.edge]
    
    verts = [ed.other_vert(vcenter) for ed in edges]
    v_cos = [v.co for v in verts]
    
    N = len(edges)
    print('there are %i verts' % N)  
    n = edges.index(ed_base)
    m = edges.index(ed_unfold)
    
    edges = edges[n:] + edges[0:n]
    verts = verts[n:] + verts[0:n]
    v_cos = v_cos[n:] + v_cos[0:n]
    print([v.index for v in verts]) 
    
    reverse = -1
    if m == (n-1) % N:
        edges.reverse()
        verts.reverse()
        v_cos.reverse()
        
        edges = [edges[-1]] + edges[0:len(edges)-1]
        verts = [verts[-1]] + verts[0:len(edges)-1]
        v_cos = [v_cos[-1]] + v_cos[0:len(edges)-1]
        reverse = 1
    
    elif m != (n+1) % N:
        print('uh oh, seems like the edges loops are trouble')
    
    print([v.index for v in verts])    
    acute = False #assume it's true,
    i = 1    
    while i < len(edges)-1 and not acute:
    #for i in range(1,len(edges)-1):
        axis = vcenter.co - v_cos[i]
        print('unwrap edge axis vert is %i' % verts[i].index)
        angle = edges[i].calc_face_angle_signed()
        
        
        if edges[i].verts[1] != vcenter:
            rev2 = -1
        else:
            rev2 = 1
        q = Quaternion(axis.normalized(),rev2* reverse* angle)
        for j in range(i+1,len(edges)):
            print('changing vert %i with index %i' % (j, verts[j].index))
            v_cos[j] = q * (v_cos[j]- v_cos[i]) + v_cos[i]   
            
        acute = test_accute(vobtuse.co,v_cos[i+1], vcenter.co) 
        if acute:
            print('We found an unwrapped acute vert')
    
        i += 1
    return v_cos[i], verts[i], v_cos
    

def geodesic_walk(bme, seed, seed_location, target, target_location, subset = None, max_iters = 100):
    
    geos= dict()
    
    fixed_verts = set()
    close_edges = set() #used to flip over to get new near verts
    close = set()
    
    if subset == None:
        print('using all the verts')
        far = set(bme.verts) #can we do this?
    else:
        print('using subset of verts')
        far = set(subset)
    
    def ring_neighbors(v):
        return [e.other_vert(v) for e in v.link_edges]
    
    def calc_T(v3, v2, v1, f, ignore_obtuse = False):
        
        
        if not ignore_obtuse:
            
            if v2 not in geos:
                if not test_accute(v3.co, v1.co, v2.co):
                    print('new vert is obtuse and we made a virtual edge')
                    vco, v2, vcos  = unwrap_tri_obtuse(v1, v3, f)
                else:
                    print("V2 not in geos and triangle is not obtuse")
            
        Tv1 = geos[v1]  #potentially use custom bmesh layer instead of a dictionary
        Tv2 = geos[v2]
        
        #calucluate 2 origins which are the 2 intersections of 2 circles
        #ceneterd on v1 and v2 with radii Tv1, Tv2 respectively
        #http://mathworld.wolfram.com/Circle-CircleIntersection.html
        
        #transform points into the reference frame of v1 with v2 on x axis
        #http://math.stackexchange.com/questions/856666/how-can-i-transform-a-3d-triangle-to-xy-plane
        u = v2.co - v1.co  #x - axis
        v2x = u.length
        
        U = u.normalized()
        
        c = v3.co - v1.co
        w = u.cross(c)  #z axis
        
        W = w.normalized()
        V = U.cross(W)  #y axis   x,y,z = u,v,w
        
        #rotation matrix from principal axes
        T = Matrix.Identity(3)  #make the columns of matrix U, V, W
        T[0][0], T[0][1], T[0][2]  = U[0] ,V[0],  W[0]
        T[1][0], T[1][1], T[1][2]  = U[1], V[1],  W[1]
        T[2][0] ,T[2][1], T[2][2]  = U[2], V[2],  W[2]

        v3p = T.transposed() * c        
        #print('converted vector to coordinates on Vo so Z should be 0')
        #print(v3p)
        #solution to the intersection of the 2 circles
        A = 2 * Tv1**2 * v2x**2 - v2x**4 + 2 * Tv2**2 * v2x**2
        B = (Tv1**2 - Tv2**2)**2
        
        x = 1/2 * (v2x**2 + Tv1**2 - Tv2**2)/(v2x)
        y = 1/2 * ((A-B)**.5)/v2x

        if isinstance(x, complex):
            print('x is complex')
            print(x)
        elif isinstance(y, complex):
            print('y is complex, setting to 0')
            print(A-B)
            print(y)
            y = 0
        T3a = v3p - Vector((x,y,0))
        T3b = v3p - Vector((x,-y,0))
        T3 = max(T3a.length, T3b.length)
        
        return T3
        
            
    def next_vert(ed,face):
        next_fs = [f for f in ed.link_faces if f != face]
        if not len(next_fs): return None
        f = next_fs[0]
        v = [v for v in f.verts if v not in ed.verts][0]
        return v
          
    if isinstance(seed, bmesh.types.BMVert):
        #initiate seeds with 0 values
        fixed_verts.add(seed)
        geos[seed] = 0
        
        vs = ring_neighbors(seed)
        
        #v = min(vs, key = lambda x: (x.co - seed.co).length)
        
        
        
        
        for v in vs:
            geos[v] = (v.co - seed.co).length  #euclidian distance to initialize
        
        fixed_verts.update(vs)
        
        #trial_v = min(vs, key = geos.get)
        #print('the closest vert to seed is %i with distance %f' % (trial_v.index, geos[trial_v]))
        
        #fixed_verts.add(trial_v)
        
        #close.update(vs)
        #close.remove(trial_v)
        
        #this way does not work because euclidian distnaces with create 0 radius
        #circles
        #ed = [e for e in seed.link_edges if e.other_vert(seed) == trial_v][0]
        #for f in ed.link_faces:
        #    nv = next_vert(ed,f)
        #    if nv:
        #        close.add(nv)
        #        v1 = seed
        #        v2 = trial_v
        
        #        T = calc_T(nv, v2, v1, f)
        #        if nv in geos:
        #            geos[nv] = max(geos[nv],T)  #perhaps min() is better but its supposed to be monotonicly increasing!
        #        else:
        #            geos[nv] = T
        
        #old method, adding all link  faces to fixed
        for f in seed.link_faces:
            for e in f.edges:
                if e not in seed.link_edges:  #the edges which make perpendiculars
                    close_edges.add(e)
                    nv = next_vert(e,f)
                    if nv:
                        close.add(nv)
                        v1 = min(e.verts, key = geos.get)
                        v2 = max(e.verts, key = geos.get)
                        ef = [fc for fc in e.link_faces if fc != f][0]
                        T = calc_T(nv, v2, v1, ef, ignore_obtuse = True)
                        if nv in geos:
                            geos[nv] = min(geos[nv],T)  #perhaps min() is better but its supposed to be monotonicly increasing!
                        else:
                            geos[nv] = T
        
    elif isinstance(seed, bmesh.types.BMFace):
        pass
    
        
    def begin_loop():
        
        for v in close:
            if v not in geos:
                print("%i not in geos but is in close" % v.index)
                
        trial_v = min(close, key = geos.get)  #Let Trial be the vertex in close with the smallest T value
        
        if max_iters != None and max_iters < 100:
            print('Trial V is %i with T: %f' % (trial_v.index, geos[trial_v]))
        
        fixed_verts.add(trial_v) #add thsi vertex to Fixed
        close.remove(trial_v)  #remove it from close
        
        #Compute the distance values for all vertices from Close (UNION) Unprocessed which are
        #incident to triangles containing Trial and another vertex in fixed
        
        for f in trial_v.link_faces:
            fvs = [v for v in f.verts if v!= trial_v and v in fixed_verts]  #all link faces have Trial as one vert.  need exactly 1 fixed_vert
            cvs = [v for v in f.verts if v!= trial_v and v not in fixed_verts]
            if len(fvs) == 1:
                if len(cvs) != 1:  print('not one close vert in the triangle, what the heck')
                cv = cvs[0]
                fv = fvs[0]
                
                if cv not in close:
                    close.add(cv)
                    far.remove(cv)
                    
                    
                T = calc_T(cv, trial_v, fv, f)
                if cv in geos:
                    #print('close vert already calced before')
                    if T != geos[cv]:
                        #print('and the distance value is changing! %f, %f' % (geos[cv],T))
                        geos[cv] = min(geos[cv],T)  #maybe min?
                else:
                    geos[cv] = T
                    
    iters = 0                
    while len(far) and len(close) and ((max_iters and iters < max_iters) or max_iters == None):
        begin_loop()
        iters += 1
        
    return geos, fixed_verts, close,    
        

def gradient_face(f, geos):
    
    #http://saturno.ge.imati.cnr.it/ima/personal-old/attene/PersonalPage/pdf/steepest-descent-paper.pdf
    [vi, vj, vk] = f.verts
    
    
    U = vj.co - vi.co
    V = vk.co - vj.co
    N = U.cross(V)
    N.normalize()
    
    
    
    T = Matrix.Identity(3)  #make the columns of matrix U, V, W
    T[0][0], T[0][1], T[0][2]  = U[0] ,U[1],  U[2]
    T[1][0], T[1][1], T[1][2]  = V[0], V[1],  V[2]
    T[2][0] ,T[2][1], T[2][2]  = N[0], N[1],  N[2]
    
    GeoV = Vector((geos[vj]-geos[vi],
                   geos[vk]-geos[vj],
                   0))
    
    
    grad = T.inverted() * GeoV
    grad.normalize()
    
    return grad


def gradient_descent_on_verts(bme, geos, start_vert, epsilon = .0000001):
    
    def ring_neighbors(v):
        return [e.other_vert(v) for e in v.link_edges]
    
    
    def grad_f_ed(f, ed, p):
        
        g = gradient_face(f, geos)
        L = g.calc_perimeter()
        
        tests = [e for e in f.edges if e != ed]
        
        for e in tests:
            
            v0, v1 = intersect_line_line(ed.verts[0].co, ed.verts[1].co, p, p-l*g)
            
            V = v0 - ed.verts[0].co
            edV = ed.verts[1].co - ed.verts[0].co
            if V.length - edV.length > epsilon:
                print('intersects outside segmetn')
            elif V.dot(edV) < 0:
                print('intersects behind')
            else:
                
                return v0, e
        
        
        
    path = [start_vert]

    
    f_start = min(start_vert.link_faces, key = lambda f: sum([geos[v] for v in f.verts]))
    
    
    iters = 0
    while True and iters < 1000:
        
        vs = [v for v in ring_neighbors(path[-1]) if v in geos]
        v = min(vs, key = geos.get)
        
        if geos[v] < geos[path[-1]]:
        #if v not in path:
            path += [v]
        else:
            break
        iters += 1
        
    return path  
        
def prepare_bmesh_for_geodesic(bme, qmeth = 0):
    '''
    will triangulate any quads
    will bisect any obtuse triangles
    '''
    start = time.time()
    
    bme.faces.ensure_lookup_table()
    
    
    not_tris = [f for f in bme.faces if len(f.verts)>3]
    bmesh.ops.triangulate(bme, faces = not_tris, quad_method = qmeth)
    
    bme.faces.ensure_lookup_table()
    bme.edges.ensure_lookup_table()
    bme.verts.ensure_lookup_table()
    
    '''
    bisect_edges = []
    bisect_inds = []
    bisect_locations = dict()

    for f in bme.faces:
        obtuse, v_ind, e_ind, bisect = test_obtuse(f)
        if obtuse:
            if e_ind in bisect_locations:
                print('found twice!')
                bisect_locations[e_ind] += [bisect]
                
            else:
                bisect_edges += [bme.edges[e_ind]]
                bisect_locations[e_ind] = [bisect]
                bisect_inds += [e_ind]  #this keeps the order in which we bisec the edge
                
    geom = bmesh.ops.bisect_edges(bme, edges = bisect_edges, cuts = 1)
    new_bmverts = [ele for ele in geom['geom_split'] if isinstance(ele, bmesh.types.BMVert)]

    #assign new verts their locations
    for v, e_ind in zip(new_bmverts, bisect_inds):
        
        #do this very explicity for error detection
        co = Vector((0,0,0))
        n = 0
        for b_loc in bisect_locations[e_ind]:
            if not isinstance(b_loc, Vector):
                print('not a vector')
            co += b_loc
            n += 1
        co = 1/n * co
        
        v.co = co
    
    #now, triangulate those faces which because quads due to bissection    
    bme.faces.ensure_lookup_table()    
    not_tris = [f for f in bme.faces if len(f.verts)>3]
    bmesh.ops.triangulate(bme, faces = not_tris)
    '''
    
    finish = time.time()
    elapsed = finish - start
    print('took %f seconds to preprocess triangles' % elapsed)