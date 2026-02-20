/**
 * @author sunag / http://www.sunag.com.br/
 */

THREE.SkeletonUtils = {

	retarget: function ( target, source, options ) {

		options = options || {};
		options.preserveMatrix = options.preserveMatrix !== undefined ? options.preserveMatrix : true;
		options.preservePosition = options.preservePosition !== undefined ? options.preservePosition : true;
		options.preserveHipPosition = options.preserveHipPosition !== undefined ? options.preserveHipPosition : false;
		options.useTargetMatrix = options.useTargetMatrix !== undefined ? options.useTargetMatrix : false;
		options.hip = options.hip !== undefined ? options.hip : "hip";
		options.names = options.names || {};

		var sourceBones = source.isObject3D ? source.skeleton.bones : this.getBones( source ),
			bones = target.isObject3D ? target.skeleton.bones : this.getBones( target );

		var bindBones,
			bone, boneTo,
			bonesPosition;

		// reset bones

		if ( target.isObject3D ) {

			target.skeleton.pose();

		} else {

			options.useTargetMatrix = true;
			options.preserveMatrix = false;

		}

		if ( options.preservePosition ) {

			bonesPosition = [];

			for ( var i = 0; i < bones.length; i ++ ) {

				bonesPosition.push( bones[ i ].position.clone() );

			}

		}

		if ( options.preserveMatrix ) {

			// reset matrix

			target.updateMatrixWorld();

			target.matrixWorld.identity();

			// reset children matrix

			for ( var i = 0; i < target.children.length; ++ i ) {

				target.children[ i ].updateMatrixWorld( true );

			}

		}

		if ( options.offsets ) {

			bindBones = [];

			for ( var i = 0; i < bones.length; ++ i ) {

				bone = bones[ i ];
				boneTo = this.getBoneByName( options.names[ bone.name ] || bone.name, sourceBones );

				if ( boneTo ) {

					bindBones.push( {
						bone: bone,
						boneTo: boneTo
					} );

				}

			}

		} else {

			bindBones = [];

			for ( var i = 0; i < bones.length; ++ i ) {

				bone = bones[ i ];
				boneTo = sourceBones[ i ];

				bindBones.push( {
					bone: bone,
					boneTo: boneTo
				} );

			}

		}

		for ( var i = 0; i < bindBones.length; ++ i ) {

			bone = bindBones[ i ].bone;
			boneTo = bindBones[ i ].boneTo;

			if ( boneTo ) {

				boneTo.updateMatrixWorld();

				if ( options.useTargetMatrix ) {

					bone.matrix.copy( boneTo.matrix );

				} else {

					bone.matrix.copy( boneTo.matrixWorld );

				}

				if ( options.preserveMatrix ) {

					bone.matrix.multiply( target.matrix.getInverse( target.matrix ) );

				}

				bone.matrix.decompose( bone.position, bone.quaternion, bone.scale );

				bone.updateMatrixWorld();

			}

		}

		if ( options.preserveHipPosition ) {

			var hips = this.getBoneByName( options.hip, bones );

			if ( hips ) {

				hips.position.set( 0, hips.position.y, 0 );

			}

		}

		if ( options.preservePosition ) {

			for ( var i = 0; i < bones.length; ++ i ) {

				bone = bones[ i ];
				bone.position.copy( bonesPosition[ i ] );

			}

		}

		if ( options.preserveMatrix ) {

			// restore matrix

			target.updateMatrixWorld( true );

		}

	},

	retargetClip: function ( target, source, clip, options ) {

		options = options || {};
		options.useFirstFramePosition = options.useFirstFramePosition !== undefined ? options.useFirstFramePosition : false;
		options.fps = options.fps !== undefined ? options.fps : 30;
		options.names = options.names || [];

		if ( ! source.isObject3D ) {

			source = this.getHelperFromSkeleton( source );

		}

		var numFrames = Math.round( clip.duration * ( options.fps / 1000 ) * 1000 ),
			delta = 1 / options.fps,
			convertedTracks = [],
			mixer = new THREE.AnimationMixer( source ),
			bones = this.getBones( target.skeleton ),
			boneDatas = [];

		for ( var i = 0; i < numFrames; ++ i ) {

			mixer.setTime( i * delta );

			this.retarget( target, source, options );

			for ( var j = 0; j < bones.length; ++ j ) {

				var bone = bones[ j ];
				boneDatas[ j ] = boneDatas[ j ] || [];
				boneDatas[ j ].push( bone.position.toArray() );
				boneDatas[ j ].push( bone.quaternion.toArray() );

			}

		}

		for ( var i = 0; i < bones.length; ++ i ) {

			var name = bones[ i ].name;

			convertedTracks.push( this.getTrack(
				".bones[" + name + "].position",
				THREE.VectorKeyframeTrack,
				boneDatas[ i ],
				delta
			) );

			convertedTracks.push( this.getTrack(
				".bones[" + name + "].quaternion",
				THREE.QuaternionKeyframeTrack,
				boneDatas[ i ],
				delta
			) );

		}

		mixer.uncacheRoot( source );

		return new THREE.AnimationClip( clip.name, - 1, convertedTracks );

	},

	getTrack: function ( name, TrackType, keyframes, delta ) {

		var times = [],
			values = [],
			stride = keyframes[ 0 ].length;

		for ( var i = 0; i < keyframes.length; ++ i ) {

			times.push( i * delta );
			values.push.apply( values, keyframes[ i ] );

		}

		return new TrackType( name, times, values );

	},

	clone: function ( source ) {

		var sourceLookup = new Map();
		var cloneLookup = new Map();

		var clone = source.clone();

		parallelTraverse( source, clone, function ( sourceNode, clonedNode ) {

			sourceLookup.set( clonedNode, sourceNode );
			cloneLookup.set( sourceNode, clonedNode );

		} );

		clone.traverse( function ( node ) {

			if ( ! node.isSkinnedMesh ) return;

			var clonedMesh = node;
			var sourceMesh = sourceLookup.get( node );
			var sourceBones = sourceMesh.skeleton.bones;

			clonedMesh.skeleton = sourceMesh.skeleton.clone();
			clonedMesh.bindMatrix.copy( sourceMesh.bindMatrix );

			clonedMesh.skeleton.bones = sourceBones.map( function ( bone ) {

				return cloneLookup.get( bone );

			} );

			clonedMesh.bind( clonedMesh.skeleton, clonedMesh.bindMatrix );

		} );

		return clone;

	},

	getBones: function ( skeleton ) {

		return Array.isArray( skeleton ) ? skeleton : skeleton.bones;

	},

	getBoneByName: function ( name, skeleton ) {

		for ( var i = 0, bones = this.getBones( skeleton ); i < bones.length; i ++ ) {

			if ( name === bones[ i ].name )

				return bones[ i ];

		}

	},

	getNearestBone: function ( bone, names ) {

		if ( names.some( function ( name ) { return bone.name === name; } ) ) return bone;

		if ( bone.parent ) return this.getNearestBone( bone.parent, names );

	},

	getEqualsBonesNames: function ( skeleton, targetSkeleton ) {

		var sourceBones = this.getBones( skeleton ),
			targetBones = this.getBones( targetSkeleton ),
			bones = [];

		search : for ( var i = 0; i < sourceBones.length; i ++ ) {

			var boneName = sourceBones[ i ].name;

			for ( var j = 0; j < targetBones.length; j ++ ) {

				if ( boneName === targetBones[ j ].name ) {

					bones.push( boneName );

					continue search;

				}

			}

		}

		return bones;

	},

	renameBones: function ( skeleton, names ) {

		var bones = this.getBones( skeleton );

		for ( var i = 0; i < bones.length; i ++ ) {

			var bone = bones[ i ];

			if ( names[ bone.name ] !== undefined ) {

				bone.name = names[ bone.name ];

			}

		}

		return this;

	},

	getHelperFromSkeleton: function ( skeleton ) {

		var source = new THREE.Object3D();
		source.skeleton = skeleton;

		for ( var i = 0; i < skeleton.bones.length; i ++ ) {

			var bone = skeleton.bones[ i ];

			var boneHelper = new THREE.Object3D();
			boneHelper.position.copy( bone.position );
			boneHelper.quaternion.copy( bone.quaternion );

			source.add( boneHelper );

		}

		source.updateMatrixWorld();

		return source;

	}

};

function parallelTraverse( a, b, callback ) {

	callback( a, b );

	for ( var i = 0; i < a.children.length; i ++ ) {

		parallelTraverse( a.children[ i ], b.children[ i ], callback );

	}

}
